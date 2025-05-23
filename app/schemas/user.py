from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = "user"
    password: str

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    address: Optional[str]
    role: str
    uploaded_face_path: Optional[str] = None
    face_encoding: Optional[str] = None
    is_face_verified: Optional[bool] = False
    created_at: datetime

    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead
    
class UserFaceVerificationUpdate(BaseModel):
    uploaded_face_path: Optional[str] = None
    face_encoding: Optional[str] = None
    is_face_verified: Optional[bool] = False
    
class FaceVerifyResponse(BaseModel):
    data: UserFaceVerificationUpdate
    message: str