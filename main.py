import random
from fastapi import FastAPI, Depends, Request
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, sessionmaker, Session, declarative_base
from faker import Faker
from slowapi import Limiter
from slowapi.util import get_remote_address

# --- DB & APP SETUP ---
Base = declarative_base()
engine = create_engine("sqlite:///./mockme_pro.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
fake = Faker()
app = FastAPI(title="MockMe Pro: The Ecosystem API")
limiter = Limiter(key_func=get_remote_address)

# --- MODELS (The "Smart" Structure) ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    job = Column(String)
    avatar = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="employees")

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    catchphrase = Column(String)
    employees = relationship("User", back_populates="company")
    products = relationship("Product", back_populates="manufacturer")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Float)
    company_id = Column(Integer, ForeignKey("companies.id"))
    manufacturer = relationship("Company", back_populates="products")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- SMART ENDPOINTS ---

@app.post("/v1/generate/ecosystem")
@limiter.limit("5/minute")
def generate_full_world(request: Request, db: Session = Depends(get_db)):
    """Creates a linked Company, User, and 3 Products in one shot."""
    
    # 1. Create Company
    new_company = Company(name=fake.company(), catchphrase=fake.bs().title())
    db.add(new_company)
    db.flush() # Gets the ID without committing yet

    # 2. Create User (CEO) linked to Company
    avatar = f"https://api.dicebear.com/7.x/bottts/svg?seed={fake.word()}"
    new_user = User(name=fake.name(), job=fake.job(), avatar=avatar, company_id=new_company.id)
    db.add(new_user)

    # 3. Create 3 Smart Products
    for _ in range(3):
        p_name = f"{new_company.name} {fake.word().capitalize()} {random.choice(['Pro', 'Max', 'Ultra'])}"
        new_product = Product(title=p_name, price=round(random.uniform(10, 999), 2), company_id=new_company.id)
        db.add(new_product)

    db.commit()
    return {"status": "Ecosystem Created", "company": new_company.name, "ceo": new_user.name}

@app.get("/v1/universe")
def get_everything(db: Session = Depends(get_db)):
    """The 'God View' - returns all linked data."""
    return {
        "users": db.query(User).all(),
        "companies": db.query(Company).all(),
        "products": db.query(Product).all()
    }