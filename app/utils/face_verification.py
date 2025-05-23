import shutil
from fastapi import UploadFile
from mtcnn import MTCNN
import cv2
import numpy as np

def save_upload_file(upload_file: UploadFile, destination: str):
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

def detect_faces(image_path):
    #Đọc ảnh từ file
    img = cv2.imread(image_path)

    if img is None:
        print("Không đọc được ảnh, kiểm tra lại đường dẫn")
        return []

    # Chuyển ảnh từ BGR (OpenCV) sang RGB (MTCNN dùng)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Khởi tạo detector MTCNN
    detector = MTCNN()
    # Phát hiện khuôn mặt, kết quả là list các dict
    faces = detector.detect_faces(img_rgb)
    
     # Tạo bản sao để vẽ, giữ nguyên img gốc
    # img_copy = img.copy()

    # Vẽ khung hình chữ nhật quanh từng khuôn mặt
    # for face in faces:
    #     x, y, width, height = face['box']
    #     cv2.rectangle(img_copy, (x, y), (x+width, y+height), (0, 255, 0), 2)

    # Hiển thị ảnh sau khi vẽ
    # cv2.imshow("Faces detected", img_copy)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    return faces


# Hàm so sánh khuôn mặt sử dụng vector đặc trưng (embedding) từ MTCNN
# Giả sử detect_faces trả về vector embedding (list hoặc numpy array)
# def compare_mtcnn_faces(face1, face2, threshold=0.6):
#     face1 = np.array(face1)
#     face2 = np.array(face2)
#     distance = np.linalg.norm(face1 - face2)
#     return distance < threshold
