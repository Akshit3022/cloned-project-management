from django.shortcuts import render
from rest_framework import viewsets
from app.models import *
from app.serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
# import requests

# Create your views here.

class RegisterView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class LoginView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request):
        userEmail = request.data.get('userEmail')
        userPassword = request.data.get('userPassword')

        try:
            user = get_object_or_404(CustomUser, userEmail=userEmail)
        except CustomUser.DoesNotExist:
            return Response({'error': 'user does not exist'}, status=status.HTTP_401_UNAUTHORIZED)

        if userPassword == user.userPassword:
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

class CustomUserView(viewsets.ViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def list(self, request):
        queryset = CustomUser.objects.all()
        serialized_data = self.serializer_class(queryset, many=True).data
        user_data = [{'userName': user['userName'], 'userType': user['userType'], 'is_active': user['is_active']} for user in serialized_data]
        return Response(user_data)


class ProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

