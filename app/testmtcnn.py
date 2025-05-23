from mtcnn import MTCNN
import cv2
import numpy as np

detector = MTCNN()
img = cv2.imread('D:/py/274762356_637953990769350_7500264676438793517_n.jpg')
result = detector.detect_faces(img)
for face in result:
        x, y, width, height = face['box']
        cv2.rectangle(img, (x, y), (x+width, y+height), (0, 255, 0), 2)
    
keypoints = face['keypoints']
# Vẽ điểm mắt, mũi, miệng
cv2.circle(img, keypoints['left_eye'], 2, (0, 0, 255), 2)
cv2.circle(img, keypoints['right_eye'], 2, (0, 0, 255), 2)
cv2.circle(img, keypoints['nose'], 2, (255, 0, 0), 2)
cv2.circle(img, keypoints['mouth_left'], 2, (255, 0, 0), 2)
cv2.circle(img, keypoints['mouth_right'], 2, (255, 0, 0), 2)
cv2.imshow("Faces detected", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(result)
