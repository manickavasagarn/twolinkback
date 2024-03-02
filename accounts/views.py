from django.shortcuts import render, redirect
from django.core.files.images import ImageFile
from django.contrib import messages
from django.contrib.auth.models import User, auth
from PIL import Image
import face_recognition
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserImage1
import json
import numpy as np
import os
import io
from rest_framework.decorators import api_view
from django.core.files import File
from django.http import HttpResponse
from django.conf import settings

BASE_DIR = settings.BASE_DIR
MEDIA_ROOT = settings.MEDIA_ROOT

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            try:
                user_image = UserImage1.objects.get(user=user)
                image_url = request.build_absolute_uri(user_image.image.url)
            except UserImage1.DoesNotExist:
                image_url = 'C:/Users/Dataaces_User/InMySight/static/userimage/thekingslayergmail.com.jpg'  # Replace with the actual path or URL of the default image
            if user.is_staff:
                return JsonResponse({'detail': 'Success examiner', 'first_name': user.first_name, 'image_url': image_url}, status=200)
            else:
                return JsonResponse({'detail': 'Success student', 'first_name': user.first_name, 'image_url': image_url}, status=200)
        else:
            return JsonResponse({'detail': 'Invalid credentials'}, status=200)
    else:
        return JsonResponse({'detail': 'Invalid request'}, status=200)




@csrf_exempt
def register(request):
    if request.method == 'POST':
        # Handle the form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        staff = request.POST.get('user_type')

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                return JsonResponse({'detail': 'Username Taken'}, status=200)
            elif User.objects.filter(email=email).exists():
                return JsonResponse({'detail': 'Email ID has already been registered'}, status=200)
            else:
                is_staff = staff == "examiner" 
                if is_staff:
                    user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name,is_staff=is_staff)
                    user.save()
                else :
                    user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                    user.save()

                # Handle the image upload
                image = request.FILES['image']

                # Load the image with face_recognition
                image_data = image.read()
                loaded_image = face_recognition.load_image_file(io.BytesIO(image_data))

                # Generate the face encoding
                encodings = face_recognition.face_encodings(loaded_image)
                if len(encodings) > 0:
                    encoding = encodings[0].tolist()  # Convert the numpy array to a list
                else:
                    encoding = None

                # Convert the list to a string
                encoding_str = json.dumps(encoding)

                # Create the UserImage1 object
                user_image = UserImage1(user=user, image=image, encoding=encoding_str, encoding2=encoding_str)
                user_image.save()

                return JsonResponse({'detail': 'User created'}, status=200)
        else:
            return JsonResponse({'detail': 'Passwords not matching'}, status=200)
    else:
        return JsonResponse({'detail': 'Invalid request'}, status=200)

@csrf_exempt
def logout(request):
    auth.logout(request)
    return JsonResponse({'detail': 'Logged out'}, status=200)


def recognize_face(request):
    if request.method == 'POST':
        # Handle the image upload
        image = request.FILES['image']

        # Load the image with face_recognition
        image_data = image.read()
        loaded_image = face_recognition.load_image_file(io.BytesIO(image_data))

        # Generate the face encoding
        unknown_face_encodings = face_recognition.face_encodings(loaded_image)
        if len(unknown_face_encodings) > 0:
            unknown_face_encoding = unknown_face_encodings[0]
        else:
            return JsonResponse({'detail': 'No face detected in the image'}, status=200)

        # Compare the face encoding with the encodings in the databasE         
        for user_image in UserImage1.objects.all():
            if user_image.encoding:  # Add this line
                known_face_encoding_list = json.loads(user_image.encoding2)  # Load the string as a list
                known_face_encoding = np.array(known_face_encoding_list)  # Convert the list to a numpy array
                matches = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding, tolerance=0.3)
                if True in matches:
                    user = user_image.user
                    auth.login(request, user)
                    try:
                        user_image = UserImage1.objects.get(user=user)
                        image_url = request.build_absolute_uri(user_image.image.url)
                    except UserImage1.DoesNotExist:
                        image_url = 'C:/Users/Dataaces_User/InMySight/static/userimage/thekingslayergmail.com.jpg'
                    if user.is_staff:
                        return JsonResponse({'detail': 'Success examiner', 'first_name': user.first_name, 'image_url': image_url}, status=200)
                    else:
                        return JsonResponse({'detail': 'Success student', 'first_name': user.first_name, 'image_url': image_url}, status=200)

        return JsonResponse({'detail': 'No match found'}, status=200)
    else:
        return JsonResponse({'detail': 'Invalid request'}, status=400)
    

@csrf_exempt
def newRegister(request):
    if request.method == 'POST':
        # Handle the form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        staff = request.POST.get('user_type')

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                return JsonResponse({'detail': 'Username Taken'}, status=200)
            elif User.objects.filter(email=email).exists():
                return JsonResponse({'detail': 'Email ID has already been registered'}, status=200)
            else:
                is_staff = staff == "examiner" 
                if is_staff:
                    user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name,is_staff=is_staff)
                    user.save()
                else :
                    user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                    user.save()

                # Handle the image upload
                image = request.FILES['image']

                # Load the image with face_recognition
                image_data = image.read()
                loaded_image = face_recognition.load_image_file(io.BytesIO(image_data))

                # Generate the face encoding
                encodings = face_recognition.face_encodings(loaded_image)
                if len(encodings) > 0:
                    encoding = encodings[0].tolist()  # Convert the numpy array to a list
                else:
                    encoding = None

                # Convert the list to a string
                encoding_str = json.dumps(encoding)

                # Create the UserImage1 object
                user_image = UserImage1(user=user, image=image, encoding=encoding_str, encoding2=encoding_str)
                user_image.save()

                user = auth.authenticate(username=username, password=password1)
                auth.login(request, user)

                user_image = UserImage1.objects.get(user=user)
                image_url = request.build_absolute_uri(user_image.image.url)
                return JsonResponse({'detail': 'Success student', 'first_name': user.first_name, 'image_url': image_url}, status=200)
        else:
            return JsonResponse({'detail': 'Passwords not matching'}, status=200)
    else:
        return JsonResponse({'detail': 'Invalid request'}, status=200)
    
@api_view(['GET'])
def DownloadPDF(self):
    path_to_file = settings.MEDIA_ROOT + '/paper.pdf'
    f = open(path_to_file, 'rb')
    pdfFile = File(f)
    response = HttpResponse(pdfFile.read())
    filename = os.path.basename(path_to_file)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response