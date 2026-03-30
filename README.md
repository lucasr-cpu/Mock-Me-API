# Mock-Me-API

A simple, open FastAPI application for generating mock user data for testing purposes. This API is publicly accessible but includes rate limiting to prevent abuse.

## Features

- **Rate Limiting**: 10 requests per minute per IP address using SlowAPI
- **Fake Data Generation**: Uses the Faker library to generate realistic user data
- **FastAPI Framework**: Built with FastAPI for high performance and automatic API documentation

## Endpoints

### GET /
Returns a welcome message indicating the API is public and rate-limited.

**Response:**
```json
{
  "message": "API is Public and Rate-Limited"
}
```

### GET /v1/generate/user
Generates a random user profile with fake data.

**Rate Limit:** 10 requests per minute per IP

**Response:**
```json
{
  "id": "uuid-string",
  "name": "Fake Name",
  "email": "fake.email@example.com",
  "username": "fake_username"
}
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

Once running, visit `http://127.0.0.1:8000/docs` for interactive API documentation provided by FastAPI.

## Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `faker`: Fake data generation
- `slowapi`: Rate limiting
