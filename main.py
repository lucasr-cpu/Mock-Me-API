import random
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.security import APIKeyHeader
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

# --- API KEY SECURITY ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# --- DATABASE MODELS ---
class Developer(Base):
    __tablename__ = "developers"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    items = relationship("StoredData", back_populates="owner", cascade="all, delete-orphan")

class StoredData(Base):
    __tablename__ = "stored_data"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    sub_category = Column(String)
    content = Column(JSON)
    dev_id = Column(Integer, ForeignKey("developers.id", ondelete="CASCADE"))
    owner = relationship("Developer", back_populates="items")

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_current_developer(api_key: str = Depends(api_key_header), db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required")
    dev = db.query(Developer).filter(Developer.api_key == api_key).first()
    if not dev:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return dev

# --- THE MEGA REGISTRY (The "Endless" Data Map) ---
# You can add 100s of lines here to expand the API's power
# WARNING: Sensitive data generators (credit cards, SSNs, EINs) produce obviously fake values.
# Do NOT use generated values in real payment or identity systems.
REGISTRY: Dict[str, Dict[str, Any]] = {
    "finance": {
        "cards": lambda: {"number": fake.credit_card_number(), "provider": fake.credit_card_provider(), "expiry": fake.credit_card_expire(), "security_code": fake.credit_card_security_code()},
        "transactions": lambda: {"id": str(uuid.uuid4()), "amount": f"{random.randint(10, 5000)}.{random.randint(10, 99)}", "vendor": fake.company(), "status": random.choice(["pending", "completed", "flagged"])},
        "crypto": lambda: {"wallet": fake.sha256(), "coin": random.choice(["Bitcoin", "Ethereum", "Solana"]), "code": random.choice(["BTC", "ETH", "SOL"])},
        "banking": lambda: {"iban": fake.iban(), "swift": fake.swift(), "account": fake.bban(), "bank_name": f"{fake.city()} National Bank"},
        "loans": lambda: {"id": fake.uuid4(), "type": random.choice(["Mortgage", "Auto", "Student"]), "interest_rate": f"{random.uniform(2.5, 12.0):.2f}%", "principal": random.randint(10000, 500000)}
    },
    "identities": {
        "people": lambda: {"name": fake.name(), "ssn": fake.ssn(), "dob": str(fake.date_of_birth()), "blood_group": fake.blood_group(), "avatar": f"https://i.pravatar.cc/150?u={uuid.uuid4()}"},
        "emails": lambda: {"personal": fake.email(), "work": fake.company_email(), "domain": fake.domain_name(), "disposable": fake.free_email()},
        "locations": lambda: {"address": fake.address(), "street": fake.street_address(), "city": fake.city(), "zip": fake.postcode(), "coordinates": {"lat": float(fake.latitude()), "lng": float(fake.longitude())}},
        "passports": lambda: {"number": fake.passport_number(), "issue_date": str(fake.date_this_decade()), "expiry": str(fake.date_this_century()), "country": fake.country_code()}
    },
    "business": {
        "corporate": lambda: {"name": fake.company(), "suffix": fake.company_suffix(), "industry": fake.bs().title(), "ein": fake.ein(), "catchphrase": fake.catch_phrase()},
        "hr": lambda: {"job_title": fake.job(), "salary": random.randint(50000, 180000), "department": fake.commerce_department(), "employee_id": f"EMP-{random.randint(1000, 9999)}"},
        "office": lambda: {"building": fake.building_number(), "street": fake.street_name(), "phone": fake.phone_number(), "floor": random.randint(1, 50)},
        "legal": lambda: {"entity_type": random.choice(["LLC", "Corp", "Partnership"]), "registration_no": fake.uuid4(), "compliance_status": random.choice(["active", "audit_pending"])}
    },
    "commerce": {
        "products": lambda: {"name": fake.ecommerce_name(), "price": fake.price(), "sku": fake.ean13(), "material": fake.ecommerce_material(), "image": f"https://picsum.photos/seed/{random.randint(1,999)}/400/400"},
        "orders": lambda: {"order_id": f"ORD-{fake.random_number(digits=8)}", "tracking": fake.tracking_number(), "courier": random.choice(["FedEx", "UPS", "DHL"]), "weight": f"{random.uniform(0.5, 20.0):.1f}kg"},
        "reviews": lambda: {"username": fake.user_name(), "rating": random.randint(1, 5), "text": fake.sentence(), "verified_purchase": fake.boolean()},
        "inventory": lambda: {"warehouse": fake.city(), "stock_level": random.randint(0, 1000), "reorder_point": 50, "last_restock": str(fake.date_this_year())}
    },
    "tech": {
        "networking": lambda: {"ip_v4": fake.ipv4(), "mac_address": fake.mac_address(), "user_agent": fake.user_agent(), "port": random.randint(1024, 65535)},
        "cloud": lambda: {"instance": f"ec2-{fake.word()}-{random.randint(1,9)}", "region": random.choice(["us-east-1", "eu-central-1", "ap-south-1"]), "uptime": f"{random.randint(1, 999)}h", "provider": "AWS"},
        "iot": lambda: {"device_id": fake.uuid4(), "temperature": f"{random.randint(18, 30)}°C", "status": "online", "firmware": f"v{random.randint(1, 5)}.{random.randint(0, 9)}"},
        "software": lambda: {"version": fake.bothify(text="??-####"), "license": fake.license_plate(), "build_number": random.randint(100, 5000)}
    },
    "social": {
        "posts": lambda: {"id": fake.uuid4(), "text": fake.text(max_nb_chars=280), "likes": random.randint(0, 50000), "shares": random.randint(0, 5000), "hashtags": [f"#{fake.word()}" for _ in range(3)]},
        "profiles": lambda: {"handle": f"@{fake.user_name()}", "bio": fake.sentence(), "followers": random.randint(100, 1000000), "is_verified": fake.boolean()},
        "chat": lambda: {"sender": fake.user_name(), "message": fake.sentence(), "timestamp": str(fake.time()), "read": fake.boolean()}
    },
    "gaming": {
        "stats": lambda: {"username": fake.user_name(), "level": random.randint(1, 100), "xp": random.randint(1000, 999999), "rank": random.choice(["Bronze", "Silver", "Gold", "Diamond", "Master"])},
        "inventory": lambda: {"item": fake.word().capitalize(), "rarity": random.choice(["Common", "Rare", "Epic", "Legendary"]), "durability": f"{random.randint(0, 100)}%"},
        "servers": lambda: {"server_name": f"Region-{fake.country_code()}", "latency": f"{random.randint(10, 150)}ms", "player_count": random.randint(0, 100)}
    },
    "automotive": {
        "vehicles": lambda: {"make": fake.company(), "model": fake.word().capitalize(), "year": fake.year(), "license_plate": fake.license_plate(), "vin": fake.vin()},
        "maintenance": lambda: {"last_service": str(fake.date_this_year()), "oil_life": f"{random.randint(10, 100)}%", "tire_pressure": "ok"},
        "navigation": lambda: {"destination": fake.address(), "eta": f"{random.randint(5, 60)} mins", "traffic": random.choice(["Light", "Heavy", "Stalled"])}
    },
    "health": {
        "vitals": lambda: {"bpm": random.randint(60, 140), "steps": random.randint(0, 20000), "sleep_hours": random.randint(4, 10)},
        "insurance": lambda: {"provider": f"{fake.company()} Health", "policy_no": fake.bothify(text="POL-#########"), "active": True},
        "medical": lambda: {"blood_type": fake.blood_group(), "allergies": [fake.word() for _ in range(2)], "last_checkup": str(fake.date_this_year())}
    },
    "entertainment": {
        "movies": lambda: {"title": fake.catch_phrase(), "director": fake.name(), "year": fake.year(), "rating": f"{random.uniform(1.0, 10.0):.1f}/10"},
        "music": lambda: {"track": fake.word().capitalize(), "artist": fake.name(), "genre": random.choice(["Rock", "Pop", "Jazz", "Electronic"]), "duration": f"{random.randint(2, 5)}:{random.randint(10, 59)}"},
        "books": lambda: {"title": fake.text(max_nb_chars=30), "author": fake.name(), "isbn": fake.isbn13(), "pages": random.randint(100, 1000)}
    },
    "science": {
        "space": lambda: {"planet": random.choice(["Mars", "Jupiter", "Saturn"]), "mission_name": f"Apollo-{random.randint(20, 100)}", "rocket": f"Space-{fake.word().capitalize()}"},
        "chemistry": lambda: {"element": random.choice(["Hydrogen", "Oxygen", "Carbon"]), "symbol": random.choice(["H", "O", "C"]), "ph_level": f"{random.uniform(0.0, 14.0):.1f}"},
        "environment": lambda: {"aqi": random.randint(0, 300), "humidity": f"{random.randint(10, 90)}%", "wind_speed": f"{random.randint(0, 50)}mph"}
    }
}
# --- PUBLIC API (Zero Setup, No Saving) ---
@app.get("/v1/public/{category}/{subcategory}")
@limiter.limit("30/minute")
def get_public_data(request: Request, category: str, subcategory: str, count: int = Query(5, ge=1, le=50)):
    """Anyone can use this to get high-quality mock data instantly."""
    if category not in REGISTRY or subcategory not in REGISTRY[category]:
        raise HTTPException(status_code=404, detail="Path not found. Check /v1/explore for options.")
    
    return [REGISTRY[category][subcategory]() for _ in range(count)]

# --- PRIVATE API (Account-Based, Persistent) ---
@app.post("/v1/account/{slug}/setup")
@limiter.limit("10/minute")
def create_developer_space(request: Request, slug: str, db: Session = Depends(get_db)):
    """Create a private workspace to store your mock data."""
    if db.query(Developer).filter(Developer.slug == slug).first():
        return {"message": "Account already exists.", "url": f"/v1/account/{slug}/data"}
    
    api_key = str(uuid.uuid4())
    new_dev = Developer(slug=slug, api_key=api_key)
    db.add(new_dev)
    db.commit()
    return {"status": "Success", "workspace": slug, "api_key": api_key, "message": "Your private silo is ready."}

@app.post("/v1/account/{slug}/{category}/{subcategory}/generate")
@limiter.limit("20/minute")
def generate_and_store(request: Request, slug: str, category: str, subcategory: str, count: int = Query(10, ge=1, le=100), dev: Developer = Depends(get_current_developer), db: Session = Depends(get_db)):
    """Generate data and SAVE it permanently to your account slug."""
    if dev.slug != slug:
        raise HTTPException(status_code=403, detail="API Key does not match workspace")

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
@limiter.limit("30/minute")
def get_account_data(request: Request, slug: str, category: Optional[str] = None, dev: Developer = Depends(get_current_developer), db: Session = Depends(get_db)):
    """Retrieve all data belonging to your slug."""
    if dev.slug != slug:
        raise HTTPException(status_code=403, detail="API Key does not match workspace")
    
    query = db.query(StoredData).filter(StoredData.dev_id == dev.id)
    if category:
        query = query.filter(StoredData.category == category)
    
    return {"workspace": slug, "items": [item.content for item in query.all()]}

@app.delete("/v1/account/{slug}/nuke")
@limiter.limit("5/minute")
def nuke_account(request: Request, slug: str, dev: Developer = Depends(get_current_developer), db: Session = Depends(get_db)):
    """Wipe everything in your workspace clean."""
    if dev.slug != slug:
        raise HTTPException(status_code=403, detail="API Key does not match workspace")
    
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