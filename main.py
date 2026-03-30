from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from faker import Faker

# 1. Setup the Limiter (identifies users by their IP address)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Open Mock-Me API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

fake = Faker()

@app.get("/")
def home():
    return {"message": "API is Public and Rate-Limited"}

# 2. Public Endpoint: No keys required, but limited to 10 hits per minute
@app.get("/v1/generate/user")
@limiter.limit("10/minute")
def get_user(request: Request):
    """Generates a random user for anyone who asks."""
    return {
        "id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "username": fake.user_name()
    }