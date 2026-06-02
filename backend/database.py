from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file URL for local development
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# engine manages connections to the database file
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal instances will be the actual database handles
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class which our database models will inherit from
Base = declarative_base()

# Dependency utility to safely open/close database connections per API request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()