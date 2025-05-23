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
    photo: UploadFile = File(...),
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

        # Tạo thư mục riêng cho user
        user_folder = os.path.join("face_uploads", f"user_{user_id}")
        os.makedirs(user_folder, exist_ok=True)

        # Xóa toàn bộ ảnh cũ trong thư mục user này
        for filename in os.listdir(user_folder):
            file_path = os.path.join(user_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Tạo tên file duy nhất cho ảnh mới
        temp_filename = f"face_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(user_folder, temp_filename)
        save_upload_file(photo, temp_path)

        # Phát hiện khuôn mặt
        faces = detect_faces(temp_path)

        if not faces:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Không phát hiện được khuôn mặt người")

        # Lưu path ảnh vào DB thay vì lưu faces
        db_user.uploaded_face_path = temp_path
        db.commit()

        data = UserFaceVerificationUpdate(
            uploaded_face_path=db_user.uploaded_face_path,
            face_encoding=db_user.face_encoding,
            is_face_verified=db_user.is_face_verified
        )

        return FaceVerifyResponse(
            data=data,
            message="Avt Hợp Lệ"
        )

    except HTTPException as http_exc:
        raise http_exc  # Cho FastAPI xử lý đúng mã lỗi

    except asyncio.CancelledError:
        print("Client đã hủy yêu cầu trong quá trình xử lý.")
        raise HTTPException(status_code=499, detail="Client cancelled the request")

    except Exception as e:
        print(f"Lỗi hệ thống: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi xác minh khuôn mặt")


# @router.post("/face-verify-compare/{user_id}")
# def face_verify_compare(
#     user_id: int,
#     photo: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     # Chỉ cho phép user tự xác thực khuôn mặt của mình
#     if current_user.id != user_id:
#         raise HTTPException(status_code=403, detail="Bạn không có quyền xác thực khuôn mặt người khác")

#     db_user = crud_user.get_user_by_id(db, user_id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User không tồn tại")

#     # Kiểm tra đã có khuôn mặt lưu trước đó chưa
#     if not db_user.uploaded_face_path:
#         raise HTTPException(status_code=400, detail="Chưa có dữ liệu khuôn mặt để so sánh. Hãy xác minh khuôn mặt trước.")

#     # Lưu file ảnh upload tạm thời
#     temp_filename = f"compare_{uuid.uuid4().hex}.jpg"
#     temp_path = os.path.join("temp_uploads", temp_filename)
#     os.makedirs("temp_uploads", exist_ok=True)
#     save_upload_file(photo, temp_path)

#     try:
#         # Lấy encoding/kết quả khuôn mặt từ ảnh mới
#         new_faces = detect_faces(temp_path)  # Hàm này trả về list encoding hoặc vector đặc trưng
#         if not new_faces:
#             raise HTTPException(status_code=400, detail="Không phát hiện được khuôn mặt trong ảnh gửi lên")

#         # Lấy encoding/kết quả khuôn mặt đã lưu
#         stored_faces = json.loads(db_user.uploaded_face_path)

#         # So sánh (giả sử bạn chỉ lưu 1 khuôn mặt, lấy phần tử đầu tiên)
#         is_verified = compare_mtcnn_faces(new_faces[0], stored_faces[0])  # Hàm này sẽ được định nghĩa bên dưới

#         # Nếu giống nhau thì cập nhật trạng thái xác thực
#         if is_verified:
#             db_user.is_face_verified = True
#             db.commit()
#             return {"is_face_verified": True, "message": "Xác thực khuôn mặt thành công"}
#         else:
#             return {"is_face_verified": False, "message": "Khuôn mặt không trùng khớp"}

#     finally:
#         os.remove(temp_path)

