# ==========================================
# fall_detector.py
# YOLO Pose + Fall Detection
# ==========================================

import cv2
import time

from ultralytics import YOLO

from config import (
    CONFIDENCE,
    FALL_RATIO,
    FALL_FRAMES,
    ALERT_COOLDOWN
)


class FallDetector:

    def __init__(self):

        print("กำลังโหลด YOLO Pose...")

        # โหลดโมเดล YOLO Pose
        self.model = YOLO("yolo11n-pose.pt")

        print("โหลด YOLO Pose สำเร็จ")

        # จำนวนเฟรมที่ตรวจพบว่าคนอยู่ในลักษณะล้ม
        self.fall_counter = 0

        # เวลาที่แจ้งเตือนล่าสุด
        self.last_alert_time = 0

        # สถานะการล้ม
        self.fall_detected = False


    def detect(self, frame):

        # ส่งภาพเข้า YOLO
        results = self.model(
            frame,
            conf=CONFIDENCE,
            verbose=False
        )

        # สถานะว่าตอนนี้มีคนอยู่ในท่าที่สงสัยว่าล้มหรือไม่
        fall_now = False


        # วนดูผลลัพธ์
        for result in results:

            # ไม่มี Keypoints
            if result.keypoints is None:
                continue


            # จุด Pose ทั้งหมด
            keypoints = result.keypoints.xy


            # ตรวจคนแต่ละคน
            for i in range(len(keypoints)):

                points = keypoints[i]


                # --------------------------------------
                # หาจุดของร่างกายทั้งหมด
                # --------------------------------------

                x_points = []
                y_points = []


                for point in points:

                    x = float(point[0])
                    y = float(point[1])


                    # ข้ามจุดที่ไม่มีข้อมูล
                    if x > 0 and y > 0:

                        x_points.append(x)
                        y_points.append(y)


                # ต้องมีจุดร่างกายอย่างน้อย 5 จุด
                if len(x_points) < 5:

                    continue


                # --------------------------------------
                # หาขอบเขตร่างกาย
                # --------------------------------------

                min_x = min(x_points)
                max_x = max(x_points)

                min_y = min(y_points)
                max_y = max(y_points)


                width = max_x - min_x
                height = max_y - min_y


                if height <= 0:

                    continue


                # --------------------------------------
                # คำนวณอัตราส่วน
                # --------------------------------------

                ratio = width / height


                # --------------------------------------
                # ตรวจสอบว่าร่างกายเป็นแนวนอนหรือไม่
                # --------------------------------------

                horizontal = ratio > FALL_RATIO


                # --------------------------------------
                # กรณีสงสัยว่าล้ม
                # --------------------------------------

                if horizontal:

                    fall_now = True


                    x1 = int(min_x)
                    y1 = int(min_y)

                    x2 = int(max_x)
                    y2 = int(max_y)


                    # กรอบสีแดง
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        3
                    )


                    # ข้อความ FALL?
                    cv2.putText(
                        frame,
                        "FALL?",
                        (x1, max(30, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3
                    )


                # --------------------------------------
                # กรณีปกติ
                # --------------------------------------

                else:

                    x1 = int(min_x)
                    y1 = int(min_y)

                    x2 = int(max_x)
                    y2 = int(max_y)


                    # กรอบสีเขียว
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )


        # ==========================================
        # นับจำนวนเฟรม
        # ==========================================

        if fall_now:

            self.fall_counter += 1

        else:

            # ถ้าไม่พบการล้ม
            # ลด counter ลงแทนที่จะรีเซ็ตทันที
            self.fall_counter = max(
                0,
                self.fall_counter - 2
            )


        # ==========================================
        # ยืนยันการล้ม
        # ==========================================

        if self.fall_counter >= FALL_FRAMES:

            self.fall_detected = True

        else:

            self.fall_detected = False


        # ==========================================
        # แจ้งเตือน
        # ==========================================

        if self.fall_detected:

            current_time = time.time()


            # ป้องกันแจ้งเตือนซ้ำรัว ๆ
            if (
                current_time - self.last_alert_time
                > ALERT_COOLDOWN
            ):

                self.alert()

                self.last_alert_time = current_time


        return frame


    # ==========================================
    # ฟังก์ชันแจ้งเตือน
    # ==========================================

    def alert(self):

        print()
        print("================================")
        print("⚠️  ตรวจพบการล้ม!")
        print("================================")
        print()