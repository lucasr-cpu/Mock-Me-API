from fastapi import FastAPI, HTTPException, Security, status, Query
from fastapi.security.api_key import APIKeyHeader
from faker import Faker
from typing import List

app = FastAPI(
    title="Mock-Me API",
    description="A high-performance mock data generator for developers.",
    version="1.0.0"
)

fake = Faker()

# Security Setup
API_KEY = "dev-secret-123"
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == API_KEY:
        return header_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Invalid or missing X-API-KEY"
    )

@app.get("/")
def root():
    return {"status": "online", "message": "Welcome to Mock-Me"}

@app.get("/v1/user")
def get_user(api_key: str = Security(get_api_key)):
    """Generates a full user profile."""
    return {
        "id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "username": fake.user_name(),
        "address": fake.address().replace("\n", ", "),
        "bio": fake.catch_phrase()
    }

@app.get("/v1/company")
def get_company(api_key: str = Security(get_api_key)):
    """Generates mock company data."""
    return {
        "company_name": fake.company(),
        "industry": fake.bs(),
        "slogan": fake.catch_phrase(),
        "headquarters": fake.city()
    }