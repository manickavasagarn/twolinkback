from django.urls import path
from . import views

urlpatterns = [
    # ...
    path('newRegister', views.newRegister, name='newRegister'),
    path('test_id', views.test_id, name='test_id'),
    path('section_id', views.section_id, name='section_id'),
    path('save_questions', views.save_questions, name='save_questions'),
    path('create_test', views.create_test, name='create_test'),
    path('save_answers', views.save_answers, name='save_answers'),
    path('check_test_id', views.check_test_id, name='check_test_id'),
    path('get_sections/<str:test_id>/', views.get_sections),
    path('get_questions/<str:section_id>/', views.get_questions),



    
    # ...
]
