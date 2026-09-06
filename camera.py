# ==========================================
# camera.py
# รับภาพจากกล้องโทรศัพท์ผ่าน Wi-Fi
# ==========================================

import cv2
from config import PHONE_CAMERA_URL


class Camera:

    def __init__(self):

        print("กำลังเชื่อมต่อกล้องโทรศัพท์...")
        print(PHONE_CAMERA_URL)

        self.cap = cv2.VideoCapture(PHONE_CAMERA_URL)

        # พยายามตั้งค่า buffer ให้เล็ก
        # เพื่อให้ภาพหน่วงน้อยลง
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():

            print("--------------------------------")
            print("ไม่สามารถเชื่อมต่อกล้องโทรศัพท์ได้")
            print("--------------------------------")
            print("ตรวจสอบว่า:")
            print("1. โทรศัพท์กับคอมอยู่ Wi-Fi เดียวกัน")
            print("2. เปิด IP Webcam แล้ว")
            print("3. กด Start Server แล้ว")
            print("4. IP ใน config.py ถูกต้อง")
            print("--------------------------------")

        else:

            print("--------------------------------")
            print("เชื่อมต่อกล้องสำเร็จ!")
            print("--------------------------------")


    def read(self):

        ret, frame = self.cap.read()

        if not ret:

            return None

        return frame


    def release(self):

        self.cap.release()