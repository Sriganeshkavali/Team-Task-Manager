from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str  # Must be verified as 'Admin' or 'Member'

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Todo"
    due_date: Optional[date] = None
    project_id: int
    assigned_to_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdateStatus(BaseModel):
    status: str

class TaskResponse(TaskBase):
    id: int

    class Config:
        from_attributes = True

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True

# --- Token Schema ---
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None