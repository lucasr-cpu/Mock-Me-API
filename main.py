from fastapi import FastAPI
from faker import Faker

app = FastAPI()
fake = Faker()

@app.get("/")
def home():
    return {"message": "Mock-Me API is Live!"}

@app.get("/user")
def get_user():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address()
    }