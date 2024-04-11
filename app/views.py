from django.shortcuts import render
from rest_framework.views import APIView
from app.models import *
from app.serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from app.permissions import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    def post(self, request, format=None):
        serializer = RegiterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token':token, 'Successful': 'Registration Successful..!'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token':token, "Successful":"Login Successful..!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error":"Invalid Credentials..!"}, status=status.HTTP_401_UNAUTHORIZED)    
            
        
class CustomUserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,format=None):
        serializer = CustomUserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK) 


class ChangePasswordView(APIView):  
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data, context={'user' :request.user})
        serializer.is_valid(raise_exception=True)
        return Response({"Successful":"Change Password Successful..!"}, status=status.HTTP_200_OK)
    
    
class SendResetPasswordEmaiView(APIView):
    def post(self, request):
        serializer = SendResetPasswordEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"Successful":"password reset link is sent..!"}, status=status.HTTP_200_OK)


class CustomUserResetPasswordView(APIView):
    def post(self, request, user_id, token, format=None):
        serializer = CustomUserResetPasswordSerializer(data=request.data, context={'user_id': user_id, 'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({"Successful":"password reset successful..!"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            print("Refresh token", token)
            token.blacklist()
            logout(request)
            return Response({"success": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ProjectFilter(filters.FilterSet):
    project_name = filters.CharFilter(field_name='projectName', lookup_expr='icontains')
    employee_name = filters.CharFilter(field_name='projectCreator__name', lookup_expr='icontains')

    class Meta:
        model = Project
        fields = ['project_name', 'employee_name']      


class ProjectListView(ListAPIView):
    serializer_class = ProjectListSerializer
    queryset = Project.objects.all()
    filter_backends = [filters.DjangoFilterBackend] 
    filterset_class = ProjectFilter
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return self.queryset  
        else:
            raise PermissionDenied("You do not have permission to view projects.")


class projectCreateView(APIView):
    permission_classes = [CanCreateProjectPermission]

    def post(self, request):
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)   
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectCRUDView(APIView):
    permission_classes = [CanCreateProjectPermission]

    def patch(self, request, id):
        try:
            project = Project.objects.get(pk=id)
            serializer = ProjectCRUDSerializer(project, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"Success": "Changes updated successfully.", "updated_data":serializer.data}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Project does not exists."},status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            project = Project.objects.get(pk=id)    
            project.delete()
            return Response({"success": "Project deleted successfully."},status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            return Response({"error": "Project does not exists."},status=status.HTTP_404_NOT_FOUND)
        

class ProjectAllocationView(APIView):
    permission_classes = [CanAllocateProject]

    def post(self, request):
        serializer = ProjectAllocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Project allocation successful.", "allocation": serializer.data},
                        status=status.HTTP_201_CREATED)        
        
        
class EmployeeAllocationListView(APIView):
    permission_classes = [CanAllocateProject]

    def get(self, request):
        employees = CustomUser.objects.filter(userType="Employee")
        serializer = EmployeeAllocationListSerializer(employees, many=True)
        return Response(serializer.data)

