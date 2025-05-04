# backend/api/v1/api.py
from fastapi import APIRouter
from backend.api.v1.endpoints import analysis

api_router = APIRouter()

# Include endpoint routers here
api_router.include_router(analysis.router, tags=["Analysis"])