from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from typing import List

from backend import models, schemas, database

# Initialize Database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Team Task Manager API")

# Security configurations
SECRET_KEY = "SUPER_SECRET_SECURITY_KEY_KEEP_IT_SAFE"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Helper Security Functions ---
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Dependency: Current User & RBAC Authorization ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, role=role)
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required."
        )
    return current_user


# --- REST API ENDPOINTS ---

# 1. Authentication Endpoints
@app.post("/register", response_model=schemas.UserResponse, status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "username": user.username}

@app.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.User).all()


# 2. Project Management Endpoints
@app.post("/projects", response_model=schemas.ProjectResponse, status_code=201)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db), admin: models.User = Depends(require_admin)):
    new_project = models.Project(name=project.name, description=project.description)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.get("/projects", response_model=List[schemas.ProjectResponse])
def list_projects(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Project).all()


# 3. Task Management Endpoints
@app.post("/tasks", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db), admin: models.User = Depends(require_admin)):
    new_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        due_date=task.due_date,
        project_id=task.project_id,
        assigned_to_id=task.assigned_to_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks", response_model=List[schemas.TaskResponse])
def list_tasks(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Admins see everything, Members see tasks assigned to them
    if current_user.role.lower() == "admin":
        return db.query(models.Task).all()
    return db.query(models.Task).filter(models.Task.assigned_to_id == current_user.id).all()

@app.patch("/tasks/{task_id}/status", response_model=schemas.TaskResponse)
def update_task_status(task_id: int, status_update: schemas.TaskUpdateStatus, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Validation: Members can only update tasks assigned specifically to them
    if current_user.role.lower() != "admin" and task.assigned_to_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to alter this task status")
        
    task.status = status_update.status
    db.commit()
    db.refresh(task)
    return task