from fastapi import FastAPI, Request, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from faker import Faker

# 1. Setup Rate Limiter (Limits by IP address)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Secure Mock-Me API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

fake = Faker()

# 2. Security: This is the "Password" for your API
API_KEY = "super-secret-key-123" 
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def validate_api_key(header_key: str = Security(api_key_header)):
    if header_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key. You are not authorized."
        )
    return header_key

# 3. Secure Endpoint with Rate Limiting (5 per minute)
@app.get("/v1/generate/user")
@limiter.limit("5/minute")
def get_secure_user(request: Request, token: str = Security(validate_api_key)):
    """Generates a user but only if you have the key and haven't spammed us."""
    return {
        "id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "role": "Verified User"
    }

@app.get("/")
def health_check():
    return {"status": "shield-up", "message": "API is protected and ready."}