from django.urls import path, include
from app.views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'register', RegisterView, basename='registration')
router.register(r'login', LoginView, basename='login')  
router.register(r'user-list', CustomUserView, basename='user-list')  

urlpatterns = [
    path('', include(router.urls)),
]