from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead, FaceVerifyResponse, UserFaceVerificationUpdate
from app.crud import user as crud_user
from app.db.session import get_db
from app.core.security import require_role, get_current_user
from app.utils.face_verification import save_upload_file, detect_faces
import os
import uuid
import json
import asyncio

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
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="User không tồn tại"
        )
    # Kiểm tra user tồn tại
    db_user = crud_user.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    return db_user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int, 
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
):
    # Kiểm tra user tồn tại
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="User không tồn tại"
        )

    db_user = crud_user.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
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

@router.post("/face-verify/{user_id}", response_model=FaceVerifyResponse)
def face_verify(
    user_id: int,
    uploaded_face: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="User không tồn tại"
            )

        db_user = crud_user.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User không tồn tại")

        # tạo tên file tạm
        temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join("temp_uploads", temp_filename)

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs("temp_uploads", exist_ok=True)

        # Lưu file ảnh upload
        save_upload_file(uploaded_face, temp_path)

        # Phát hiện khuôn mặt
        faces = detect_faces(temp_path)

        # Xóa file tạm sau khi xử lý
        os.remove(temp_path)

        if not faces:
            raise HTTPException(status_code=400, detail="Không phát hiện được khuôn mặt người")

        db_user.uploaded_face_path = json.dumps(faces, default=str)
        db.commit()

        data = UserFaceVerificationUpdate(
            uploaded_face_path=db_user.uploaded_face_path,
            face_encoding=db_user.face_encoding,
            is_face_verified=db_user.is_face_verified
        )

        return FaceVerifyResponse(
            data=data,
            message="Xác minh khuôn mặt thành công và đã lưu ảnh"
        )

    except HTTPException as http_exc:
        raise http_exc  # Cho FastAPI xử lý đúng mã lỗi

    except asyncio.CancelledError:
        # Client cancel giữa chừng, ghi log nếu cần
        print("Client đã hủy yêu cầu trong quá trình xử lý.")
        raise HTTPException(status_code=499, detail="Client cancelled the request")

    except Exception as e:
        # Bắt các lỗi không mong muốn
        print(f"Lỗi hệ thống: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi xác minh khuôn mặt")
    