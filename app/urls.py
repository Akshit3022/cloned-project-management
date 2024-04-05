from django.urls import path, include
from app.views import *
from rest_framework import routers


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user-profile/', CustomUserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('reset-password/', SendResetPasswordEmaiView.as_view(), name='reset-password'),
]   