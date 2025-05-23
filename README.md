# UserManagement

- python version
python 3.10.0
- pip version
python 25.1.1

- tạo môi trường ảo
    python -m venv venv

- chạy môi trường ảo
    source venv/Scripts/activate

- cài FastAPI và Uvicorn
    pip install fastapi uvicorn

- chạy server
    uvicorn app.main:app --reload

- Dừng server & thoát môi trường ảo
    + Dừng server: nhấn Ctrl + C
    + Thoát môi trường ảo: deactivate

- Copy lib vào file requirements.txt
    pip freeze > requirements.txt

- cài đặt lib trong requirements
    pip install -r requirements.txt

- Cài đặt Alembic 
    pip install alembic
    - khởi tạo Alembic
        alembic init alembic
    - vào file alembic.ini
        sqlalchemy.url = sqlite:///./user_management.db
    - vào file alembic/env.py
        from app.db.base import Base
        target_metadata = Base.metadata

    - Tạo migration tự động
        alembic revision --autogenerate -m "..." (tạo bản ghi và thêm mô tả cho migration)
    - Áp dụng migration lên database
        run: alembic upgrade head


- MTCNN sử dụng mô hình tensorflow bên trong để sử lý deep learning
    pip install tensorflow
- Cài mô hinh MTCCN(Multi-task Cascaded Convolutional Networks)
    pip install mtcnn opencv-python numpy

    + mtcnn: để phát hiện khuôn mặt
    + opencv-python: để xử lý ảnh
    + numpy: hỗ trợ xử lý ảnh dưới dạng mảng