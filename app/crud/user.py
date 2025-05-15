from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

# def create_user(db: Session, user: UserCreate):
#     db_user = User(name=user.name, email=user.email)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user