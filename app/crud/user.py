from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.untils.authen import Authen

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not Authen.verify_password(password, user.hashed_password):
        return None
    return user

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        address=user.address,
        role="user",
        hashed_password=Authen.get_password_hash(user.password),  # hash password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db:Session, db_user: User, user_update: UserCreate):
    db_user.name = user_update.name
    db_user.email = user_update.email
    db_user.phone = user_update.phone
    db_user.address = user_update.address
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
