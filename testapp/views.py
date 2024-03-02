from django.shortcuts import render, redirect
from django.core.files.images import ImageFile
from django.contrib import messages
from django.contrib.auth.models import User, auth
from PIL import Image
import face_recognition
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User_Data
import json
import numpy as np
import os
import io
from rest_framework.decorators import api_view
from django.core.files import File
from django.http import HttpResponse
from django.conf import settings
from .models import Test_Info
from .models import Test_Questions,Test_Evaluation
import string
import random
# Create your views here.
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

                # Create the User_Data object
                user_image = User_Data(user=user, photo=image, encoding=encoding_str, type='face')
                user_image.save()

                user = auth.authenticate(username=username, password=password1)
                auth.login(request, user)

                user_image = User_Data.objects.get(user=user)
                image_url = request.build_absolute_uri(user_image.photo.url)
                return JsonResponse({'detail': 'Success student', 'first_name': user.first_name, 'image_url': image_url}, status=200)
        else:
            return JsonResponse({'detail': 'Passwords not matching'}, status=200)
    else:
        return JsonResponse({'detail': 'Invalid request'}, status=200)


@csrf_exempt
def generate_id(size=4, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

@csrf_exempt  
def test_id(request):
    while True:
        id = generate_id() + "-" + generate_id(3) + "-" + generate_id()
        if not Test_Info.objects.filter(test_id=id).exists():
            break
    return JsonResponse({'unique_id': id})

@csrf_exempt
def section_id(request):
    while True:
        id = generate_id() + "-" + generate_id(3) + "-" + generate_id()
        if not Test_Questions.objects.filter(section_id=id).exists():
            break
    return JsonResponse({'unique_id': id})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Test_Questions
import json


@csrf_exempt
def save_questions(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        section_id = data.get('section_id')
        section_name = data.get('section_name')
        section_desc = data.get('section_desc')
        test_id = data.get('test_id')
        questions = data.get('questions')

        # Extract answers from questions and remove 'answer' key from each question
        answers = [q.pop('answer') for q in questions]

        # Get the Test_Info instance that corresponds to the test_id
        test_info_instance = Test_Info.objects.get(test_id=test_id)

        # Create a new Test_Questions instance
        test_questions = Test_Questions(
            test_id=test_info_instance,
            section_id=section_id,
            section_name=section_name,
            section_desc=section_desc,
            test_questions=questions,
            test_answers=answers
        )
        test_questions.save()

        return JsonResponse({'detail': 'success'})
    else:
        return JsonResponse({'detail': 'failed', 'error': 'Invalid request method'}, status=400)


    
@csrf_exempt
def create_test(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        testName = data.get('testName')
        testDesc = data.get('testDesc')
        uniqueCode = data.get('uniqueCode')

        # Create a new Test_Info instance
        test_info = Test_Info(
            test_id=uniqueCode,
            test_title=testName,
            test_desc=testDesc,
            test_url="www.sampleurl.com"
        )
        test_info.save()

        return JsonResponse({'message': 'Test created successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def save_answers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Extract the necessary data
        user = request.user
        test_id = data['test_id']
        section_id = data['section_id']
        attempted_answers = data['answers']  # Extract the answers from the data

        # Get the correct answers from Test_Questions
        test_questions = Test_Questions.objects.get(test_id=test_id, section_id=section_id)
        correct_answers = test_questions.test_answers  # test_answers is already a list

        # Compare the attempted answers with the correct answers
        test_score = sum(attempted == correct for attempted, correct in zip(attempted_answers, correct_answers))

        # Get the Test_Info instance with the given test_id
        test_info = Test_Info.objects.get(test_id=test_id)

        # Create a new Test_Evaluation instance
        evaluation = Test_Evaluation(
            test_id=test_info,  # Assign the Test_Info instance
            user=user,
            section_id=section_id,
            answers=attempted_answers,
            proctoring_score=0,  # You'll need to calculate this
            test_score=test_score,
        )
        evaluation.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed', 'error': 'Invalid request method'})
    
@csrf_exempt
def check_test_id(request):
    if request.method == 'POST':
        test_id = request.POST.get('testId')
        try:
            test_info = Test_Info.objects.get(id=test_id)
            return JsonResponse({'detail': 'ID present'}, status=200)
        except Test_Info.DoesNotExist:
            return JsonResponse({'detail': 'ID not found'}, status=404)
    else:
        return JsonResponse({'detail': 'Invalid request'}, status=400)
    

@csrf_exempt
def get_sections(request, test_id):
    # Get the Test_Questions instances that correspond to the test_id
    test_questions = Test_Questions.objects.filter(test_id=test_id)

    # Format the data
    sections = [{
        'section_id': tq.section_id,
        'section_name': tq.section_name,
        'section_desc': tq.section_desc,
        'test_questions': tq.test_questions,
    } for tq in test_questions]

    # Return the data as JSON
    return JsonResponse({'sections': sections})

@csrf_exempt
def get_questions(request, section_id):
    # Get the Test_Questions instance that corresponds to the section_id
    test_questions = Test_Questions.objects.get(section_id=section_id)

    # Format the data
    questions = {
        'section_id': test_questions.section_id,
        'section_name': test_questions.section_name,
        'section_desc': test_questions.section_desc,
        'test_questions': test_questions.test_questions,
    }

    # Return the data as JSON
    return JsonResponse(questions)


