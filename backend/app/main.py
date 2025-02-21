from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.search.elastic import init_elasticsearch
from app.db.init_db import init_db

app = FastAPI(title=settings.PROJECT_NAME)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    # Initialize databases
    await init_db()
    # Initialize Elasticsearch indices
    await init_elasticsearch()
