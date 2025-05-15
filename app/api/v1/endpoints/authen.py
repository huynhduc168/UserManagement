from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead, TokenResponse
from app.crud import user as crud_user
from app.db.session import get_db
from app.untils.jwt_token import create_access_token

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=200)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud_user.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")
    new_user = crud_user.create_user(db, user)
    return new_user

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    password = form_data.password
    user = crud_user.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Email hoặc mật khẩu không đúng")
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user)
    }