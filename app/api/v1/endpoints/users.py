from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead
from app.crud import user as crud_user
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=list[UserRead])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get list of users with pagination
    """
    return crud_user.get_users(db, skip=skip, limit=limit)

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create new user
    """
    return crud_user.create_user(db, user)