from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead
from app.crud import user as crud_user
from app.db.session import get_db
from app.core.security import require_role, get_current_user

router = APIRouter()

@router.get("/", response_model=list[UserRead])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), _ = Depends(require_role("admin"))):
    return crud_user.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
):
    # Kiểm tra user tồn tại
    db_user = crud_user.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
    # Kiểm tra quyền xem thông tin
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403, 
            detail="Bạn không có quyền xem thông tin người dùng khác"
        )
    
    return db_user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int, 
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
):
    # Kiểm tra user tồn tại
    db_user = crud_user.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
    # Kiểm tra quyền cập nhật
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403, 
            detail="Bạn không có quyền cập nhật thông tin người dùng khác"
        )
    
    # Kiểm tra email trùng lặp nếu email thay đổi
    if user.email != db_user.email:
        existing_user = crud_user.get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")
    
    updated_user = crud_user.update_user(db, db_user, user)
    return updated_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _ = Depends(require_role("admin"))):
    db_user = crud_user.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    crud_user.delete_user(db, db_user)
    return{"detail": "User đã được xóa thành công", "status": 200}