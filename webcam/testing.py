'''import cv2
import numpy as np
import face_recognition
import mediapipe as mp
import torch
import threading
from ultralytics import YOLO

camera = cv2.VideoCapture(0)
yolo_model = YOLO("yolov8s.pt")
frame = camera.read()
def gen_frames3():
    while True: 
        # Perform YOLOv8 object detection on the frame
        results = yolo_model.predict(frame)  # YOLOv8 inference
        xyxys =[]
        class_ids = []
        for result in results:
            boxes = result.boxes.cpu().numpy()
            xyxys = boxes.xyxy
            for xyxy in xyxys:
                x1, y1, x2, y2 = map(int, xyxy[:4])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


gen_frames3()'''

import cv2
import numpy as np
from ultralytics import YOLO
import threading

# Initialize the YOLO model
yolo_model = YOLO("yolov8s.pt")

# Create a flag to control the threads
stop_threads = False

frame = None

# Function to capture video on one thread
def capture_video():
    global frame
    camera = cv2.VideoCapture(0)
    while not stop_threads:
        ret, frame = camera.read()

# Function to perform YOLOv8 inference on another thread
def yolo_inference():
    global frame
    while not stop_threads:
        results = yolo_model.predict(frame)  # YOLOv8 inference
        xyxys = []
        class_ids = []
        for result in results:
            boxes = result.boxes.cpu().numpy()
            xyxys = boxes.xyxy
            for xyxy in xyxys:
                x1, y1, x2, y2 = map(int, xyxy[:4])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

# Start the video capture and YOLOv8 inference threads
video_thread = threading.Thread(target=capture_video)
yolo_thread = threading.Thread(target=yolo_inference)
video_thread.start()
yolo_thread.start()

# The code for encoding and yielding frames can remain in the main thread
def gen_frames3():
    global frame
    while not stop_threads:
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

while True:
    gen_frames3()
