import random
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Request, Query
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, create_engine, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from sqlalchemy.sql import func
from faker import Faker
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- DATABASE & CORE SETUP ---
# This creates a local SQLite database file on your laptop
DATABASE_URL = "sqlite:///./mockme_ultimate_v5.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
fake = Faker()

# --- RATE LIMITER (The Shield) ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Mock-Me Ultra: The Infinite Data Engine")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- DATABASE MODELS ---
class Developer(Base):
    __tablename__ = "developers"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    items = relationship("StoredData", back_populates="owner")

class StoredData(Base):
    __tablename__ = "stored_data"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    sub_category = Column(String)
    content = Column(JSON)
    dev_id = Column(Integer, ForeignKey("developers.id"))
    owner = relationship("Developer", back_populates="items")

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- THE MEGA REGISTRY (The "Endless" Data Map) ---
# You can add 100s of lines here to expand the API's power
REGISTRY: Dict[str, Dict[str, Any]] = {
    "finance": {
        "cards": lambda: {"number": fake.credit_card_number(), "provider": fake.credit_card_provider(), "expiry": fake.credit_card_expire(), "security_code": fake.credit_card_security_code()},
        "transactions": lambda: {"id": str(uuid.uuid4()), "amount": f"{random.randint(10, 5000)}.{random.randint(10, 99)}", "vendor": fake.company(), "status": random.choice(["pending", "completed", "flagged"])},
        "crypto": lambda: {"wallet": fake.cryptocurrency_address(), "coin": fake.cryptocurrency_name(), "code": fake.cryptocurrency_code()},
        "banking": lambda: {"iban": fake.iban(), "swift": fake.swift(), "account": fake.bban(), "bank_name": f"{fake.city()} National Bank"}
    },
    "identities": {
        "people": lambda: {"name": fake.name(), "ssn": fake.ssn(), "dob": str(fake.date_of_birth()), "blood_group": fake.blood_group(), "avatar": f"https://i.pravatar.cc/150?u={uuid.uuid4()}"},
        "emails": lambda: {"personal": fake.email(), "work": fake.company_email(), "domain": fake.domain_name(), "disposable": fake.free_email()},
        "locations": lambda: {"address": fake.address(), "coordinates": {"lat": float(fake.latitude()), "lng": float(fake.longitude())}, "timezone": fake.timezone()}
    },
    "business": {
        "corporate": lambda: {"name": fake.company(), "suffix": fake.company_suffix(), "industry": fake.bs().title(), "ein": fake.ein()},
        "hr": lambda: {"job_title": fake.job(), "salary": random.randint(50000, 180000), "department": fake.commerce_department(), "employee_id": f"EMP-{random.randint(1000, 9999)}"},
        "office": lambda: {"building": fake.building_number(), "street": fake.street_name(), "phone": fake.phone_number()}
    },
    "commerce": {
        "products": lambda: {"name": fake.ecommerce_name(), "price": fake.price(), "sku": fake.ean13(), "material": fake.ecommerce_material(), "image": f"https://picsum.photos/seed/{random.randint(1,999)}/400/400"},
        "orders": lambda: {"order_id": f"ORD-{fake.random_number(digits=8)}", "tracking": fake.tracking_number(), "courier": random.choice(["FedEx", "UPS", "DHL"])},
        "reviews": lambda: {"username": fake.user_name(), "rating": random.randint(1, 5), "text": fake.sentence()}
    },
    "tech": {
        "networking": lambda: {"ip_v4": fake.ipv4(), "mac_address": fake.mac_address(), "user_agent": fake.user_agent()},
        "cloud": lambda: {"instance": f"ec2-{fake.word()}-{random.randint(1,9)}", "region": random.choice(["us-east-1", "eu-central-1", "ap-south-1"]), "uptime": f"{random.randint(1, 999)}h"},
        "iot": lambda: {"device_id": fake.uuid4(), "temperature": f"{random.randint(18, 30)}°C", "status": "online"}
    }
}

# --- PUBLIC API (Zero Setup, No Saving) ---
@app.get("/v1/public/{category}/{subcategory}")
@limiter.limit("30/minute")
def get_public_data(request: Request, category: str, subcategory: str, count: int = Query(5, le=50)):
    """Anyone can use this to get high-quality mock data instantly."""
    if category not in REGISTRY or subcategory not in REGISTRY[category]:
        raise HTTPException(status_code=404, detail="Path not found. Check /v1/explore for options.")
    
    return [REGISTRY[category][subcategory]() for _ in range(count)]

# --- PRIVATE API (Account-Based, Persistent) ---
@app.post("/v1/account/{slug}/setup")
def create_developer_space(slug: str, db: Session = Depends(get_db)):
    """Create a private workspace to store your mock data."""
    if db.query(Developer).filter(Developer.slug == slug).first():
        return {"message": "Account already exists.", "url": f"/v1/{slug}/data"}
    
    new_dev = Developer(slug=slug)
    db.add(new_dev)
    db.commit()
    return {"status": "Success", "workspace": slug, "message": "Your private silo is ready."}

@app.post("/v1/account/{slug}/{category}/{subcategory}/generate")
def generate_and_store(slug: str, category: str, subcategory: str, count: int = 10, db: Session = Depends(get_db)):
    """Generate data and SAVE it permanently to your account slug."""
    dev = db.query(Developer).filter(Developer.slug == slug).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Workspace not found. Run /setup first.")

    if category not in REGISTRY or subcategory not in REGISTRY[category]:
        raise HTTPException(status_code=400, detail="Invalid Category/Subcategory path.")

    results = []
    for _ in range(count):
        fake_data = REGISTRY[category][subcategory]()
        new_entry = StoredData(category=category, sub_category=subcategory, content=fake_data, dev_id=dev.id)
        db.add(new_entry)
        results.append(fake_data)
    
    db.commit()
    return {"workspace": slug, "path": f"{category}/{subcategory}", "added": count, "data": results}

@app.get("/v1/account/{slug}/data")
def get_account_data(slug: str, category: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve all data belonging to your slug."""
    dev = db.query(Developer).filter(Developer.slug == slug).first()
    if not dev: return {"error": "Account not found"}
    
    query = db.query(StoredData).filter(StoredData.dev_id == dev.id)
    if category:
        query = query.filter(StoredData.category == category)
    
    return {"workspace": slug, "items": [item.content for item in query.all()]}

@app.delete("/v1/account/{slug}/nuke")
def nuke_account(slug: str, db: Session = Depends(get_db)):
    """Wipe everything in your workspace clean."""
    dev = db.query(Developer).filter(Developer.slug == slug).first()
    if dev:
        db.query(StoredData).filter(StoredData.dev_id == dev.id).delete()
        db.commit()
    return {"status": "Clean Slate", "message": f"All data for '{slug}' has been deleted."}

@app.get("/v1/explore")
def list_all_endpoints():
    """Returns a map of every single data point this API can generate."""
    return {cat: list(sub.keys()) for cat, sub in REGISTRY.items()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)