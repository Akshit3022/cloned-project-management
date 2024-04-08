from django.urls import path, include
from app.views import *
# from rest_framework import routers


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user-profile/', CustomUserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('send-password/', SendResetPasswordEmaiView.as_view(), name='send-password'),
    path('reset-password/<user_id>/<token>/', CustomUserResetPasswordView.as_view(), name='reset-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('project/', ProjectListView.as_view(), name='project-list'),
    path('project/<int:id>/', ProjectCRUDView.as_view(), name='project-update-delete'),
]   