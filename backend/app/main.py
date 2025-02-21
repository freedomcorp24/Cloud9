from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.init_db import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Cloud 9 THC/CBD Marketplace API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Root route serves HTML with links
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Cloud 9 API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                a { display: block; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>Cloud 9 API</h1>
            <a href="/docs">API Documentation (Swagger UI)</a>
            <a href="/redoc">Alternative Documentation (ReDoc)</a>
            <a href="/openapi.json">OpenAPI Schema</a>
            <a href="/api/v1/auth">Authentication Endpoints</a>
            <a href="/api/v1/products">Product Endpoints</a>
            <a href="/healthz">Health Check</a>
        </body>
    </html>
    """

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    # Initialize databases
    await init_db()
