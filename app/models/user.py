from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)
    address = Column(String(255))
    role = Column(String(100), nullable=False)
    hashed_password = Column(String(100), nullable=False)
    uploaded_face_path = Column(String(255), nullable=True)
    is_face_verified = Column(Boolean, default=False)          # Trạng thái xác thực khuôn mặt
    face_encoding = Column(LargeBinary, nullable=True)         # Encoding khuôn mặt (optional)
    created_at = Column(DateTime(timezone=True), server_default=func.now())