from django.urls import path
from . import views

urlpatterns = [
    # ...
    path('accounts/login', views.login, name='login'),
    path('accounts/register', views.register, name='register'),
    path('accounts/logout', views.logout, name='logout'),
    path('accounts/recognize_face', views.recognize_face, name='recognize_face'),
    path('accounts/DownloadPDF', views.DownloadPDF, name='DownloadPDF'),

    
    # ...
]
