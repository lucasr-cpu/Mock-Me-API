from fastapi import FastAPI, Request, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from faker import Faker
import random

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./mockme.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    avatar_url = Column(String)

Base.metadata.create_all(bind=engine)
fake = Faker()

app = FastAPI(title="Advanced Mock-Me Pro")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS ---

@app.get("/v1/generate/user")
def create_mock_user(db: Session = Depends(get_db)):
    """Generates a user, saves them to SQLite, and adds a free avatar image."""
    
    # 1. Choose a random free image service
    seed = random.randint(1, 1000)
    avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}"
    
    # 2. Create the user object
    new_user = UserDB(
        name=fake.name(),
        email=fake.email(),
        avatar_url=avatar
    )
    
    # 3. Save to SQLite
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.get("/v1/users/all")
def get_all_saved_users(db: Session = Depends(get_db)):
    """View everyone currently stored in your database."""
    return db.query(UserDB).all()