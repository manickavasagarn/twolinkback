from django.urls import path
from . import views

urlpatterns = [
    # path('home', views.home, name='home'),
    # path('video_feed', views.video_feed, name='video_feed'),
    # path('video_feed2', views.video_feed2, name='video_feed2'),
    # path('video_feed3', views.video_feed3, name='video_feed3'),
    # path('exam_terminated/', views.exam_terminated, name='exam_terminated'),
    path('process_frame', views.process_frame),
]
