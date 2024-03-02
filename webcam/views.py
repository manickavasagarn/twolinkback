import io

import face_recognition
import cv2
from django.shortcuts import render
from django.http import StreamingHttpResponse
import numpy as np
import threading
import mediapipe as mp
import requests
from ultralytics.utils.plotting import Annotator 
from ultralytics import YOLO
from multiprocessing import Process, Manager, cpu_count, set_start_method
import time
import platform
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import base64
from django.http import JsonResponse
from testapp.models import User_Data
import json
from django.contrib.auth.models import User, auth
known_face_encodings = []
known_face_names = []


def load_known_faces():
    user_image = face_recognition.load_image_file("static/userimage/Nicolas.jpeg")
    user_face_encoding = face_recognition.face_encodings(user_image)[0]


    known_face_encodings.extend([user_face_encoding])
    known_face_names.extend(["Nicolas"])
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
#yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
yolo_model = YOLO("yolov5su.pt")
yolo_model.export(format = 'openvino')
ov_model = YOLO('yolov5su_openvino_model/')

load_known_faces()
stop_threads = False

# def gen_frames3():
#     while True and not stop_threads:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             # Resize frame of video to 1/4 size for faster face recognition processing
#             small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#             # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
#             rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

#             # Only process every other frame of video to save time

#             # Find all the faces and face encodings in the current frame of video
#             face_locations = face_recognition.face_locations(rgb_small_frame)
#             face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
#             face_names = []
#             for face_encoding in face_encodings:
#                 # See if the face is a match for the known face(s)
#                 matches = face_recognition.compare_faces(known_face_encodings, face_encoding,tolerance=0.5)
#                 name = "Unknown"
#                 # Or instead, use the known face with the smallest distance to the new face
#                 face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#                 best_match_index = np.argmin(face_distances)
#                 if matches[best_match_index]:
#                     name = known_face_names[best_match_index]

#                 face_names.append(name)

#             # Display the results
#             for (top, right, bottom, left), name in zip(face_locations, face_names):
#                 # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#                 top *= 4
#                 right *= 4
#                 bottom *= 4
#                 left *= 4
#                 cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
#                 font = cv2.FONT_HERSHEY_DUPLEX
#                 cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')





# def gen_frames():
#     while True and not stop_threads:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             output = face_mesh.process(rgb_frame)
#             landmark_points = output.multi_face_landmarks
#             frame_h, frame_w, _ = frame.shape
#             if landmark_points:
#                 landmarks = landmark_points[0].landmark
#                 for landmark in landmarks[469:478]:
#                     x = int(landmark.x * frame_w)
#                     y = int(landmark.y * frame_h)
#                     cv2.circle(frame, (x, y), 3, (0, 255, 0))
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# def gen_frames2(request):
#     warning_count = 0
#     while True and not stop_threads:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             # Perform YOLOv5 object detection on the frame
#             results = ov_model.predict(frame,stream =True, conf = 0.5)  # YOLOv5 inference
#             xyxys =[]
#             classes = []
#             class_conf = []
#             for result in results:
#                 annotator = Annotator(frame)
#                 boxes = result.boxes
#                 num_people_detected = 0
#                 for box in boxes:
#                     b = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
#                     c = box.cls
#                     annotator.box_label(b, yolo_model.names[int(c)])
#                     if yolo_model.names[int(c)] == 'person':
#                         num_people_detected += 1
#                 if num_people_detected > 1 or num_people_detected == 0:
#                     warning_count += 1
#                     print(f'Warning: {num_people_detected} person(s) detected. Warning count: {warning_count}')
    
#         frame = annotator.result()
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        


# def home(request):
#     return render(request, 'home.html')

# def video_feed(request):
#     return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace;boundary=frame')

# def video_feed2(request):
#     return StreamingHttpResponse(gen_frames2(request), content_type='multipart/x-mixed-replace;boundary=frame')

# def video_feed3(request):
#     return StreamingHttpResponse(gen_frames3(), content_type='multipart/x-mixed-replace;boundary=frame')

# def exam_terminated(request):
#     return render(request, 'exam_terminated.html')

pupil_position = None
frame_count = 0

@csrf_exempt
def process_frame(request):
    global pupil_position, frame_count
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Get the uploaded file
        images = request.FILES['image']

        nparr = np.frombuffer(images.read(), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        user = auth.authenticate(username=username, password=password)

        # Perform YOLOv5 object detection on the frame
        results = ov_model.predict(frame, stream=True, conf=0.5)  # YOLOv5 inference
        num_people_detected = 0
        device_detected = False
        rgb_small_frame = np.ascontiguousarray(frame[:, :, ::-1])
        annotator = Annotator(rgb_small_frame)
        for result in results:
            boxes = result.boxes
            for box in boxes:
                b = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
                c = box.cls
                annotator.box_label(b, yolo_model.names[int(c)])
                if yolo_model.names[int(c)] == 'person':
                    num_people_detected += 1
                elif yolo_model.names[int(c)] in ['smartphone', 'laptop']:
                    device_detected = True

 
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

 
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape
        if landmark_points:
            landmarks = landmark_points[0].landmark
            if len(landmarks) > 478:  # Ensure there are enough landmarks
                for landmark in landmarks[469:478]:
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 0))

                # Assuming the iris landmark is at index 468
                iris_x = int(landmarks[468].x * frame_w)
                iris_y = int(landmarks[468].y * frame_h)
                left_eye_x = int(landmarks[469].x * frame_w)
                right_eye_x = int(landmarks[478].x * frame_w)
                pupil_distance = abs(iris_x - (left_eye_x + right_eye_x) / 2)

                # Check if the pupil has moved left or right
                if pupil_position is None:
                    pupil_position = pupil_distance
                elif abs(pupil_distance - pupil_position) > 5:  # Threshold for pupil movement
                    frame_count += 1
                    pupil_position = pupil_distance
                else:
                    frame_count = 0

        # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])


        # face_locations = face_recognition.face_locations(rgb_small_frame)
        # face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


        # user_data = User_Data.objects.get(user=user, type='face')
        # known_face_encoding = json.loads(user_data.encoding)

        # for face_encoding in face_encodings:
        #     matches = face_recognition.compare_faces([known_face_encoding], face_encoding.tolist(), tolerance=0.5)
            if frame_count > 7 or num_people_detected > 1 or device_detected:

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                user_data = User_Data(user=request.user, photo=ContentFile(frame, 'snapshot.jpg'), type='snap')
                user_data.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)