from fastapi import APIRouter, Request
from app.api.v1 import auth, auth_tor, products

api_router = APIRouter()

def is_tor_request(request: Request) -> bool:
    # Check if request is coming from Tor
    # This is a basic check - in production, you'd want more sophisticated detection
    return "tor" in request.headers.get("user-agent", "").lower()

# Regular auth endpoints for clearnet
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Tor-specific auth endpoints with rate limiting
api_router.include_router(auth_tor.router, prefix="/auth", tags=["auth"])

# Product endpoints
api_router.include_router(products.router, prefix="/products", tags=["products"])
