from fastapi import APIRouter
from app.api.v1.endpoints import users, authen

api_router = APIRouter()

# Authen
api_router.include_router(authen.router, prefix="/authen", tags=["authen"])
# Include users router
api_router.include_router(users.router, prefix="/users", tags=["users"])
