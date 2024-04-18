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
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied
from app.filters import *
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.http import JsonResponse
import stripe
from django.views.generic.base import TemplateView


stripe.api_key = settings.STRIPE_SECRET_KEY

# def create_payment_intent(request):
#     amount = 1000  
    
#     payment_intent = stripe.PaymentIntent.create(
#         amount=amount,
#         currency='inr'
#     )
    
#     return JsonResponse({
#         'client_secret': payment_intent.client_secret
#     })


class CheckPaymentView(TemplateView):
    # permission_classes = [IsAuthenticated]
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLIC_KEY
        print("context_data", context)
        return context

def message(request):
    if request.method == 'POST':
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={"token": request.POST['stripeToken']}
        )

        payment_intent = stripe.PaymentIntent.create(
            amount=25000,
            currency='inr',
            description='stripe payment intent',
            payment_method=payment_method.id,
            confirm=True,
            return_url='http://127.0.0.1:8000/api/success-message/'
    ) 
    return render(request, 'message.html')

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
        serializer.save()
        return Response({'Successful': 'Registration Successful..!'}, status=status.HTTP_201_CREATED)


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
        request.data['projectCreator'] = request.user.id
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
        print(serializer.data)
        return Response(serializer.data)

class TaskStatusView(APIView):
    permission_classes = [CanChangeTaskStatus]

    def patch(self, request, id):
        project_allocaction = ProjectAllocation.objects.get(pk=id)
        user_name = request.user.name
        serializer = TaskStatusSerializer(project_allocaction, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if project_allocaction.taskStatus == True:
            response_data = {
                "Success": f"Task has been completed successfully by {user_name}.",
                "updated_data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # return Response({"Success": "Task has been completed successfully by {{user_name}}.", "updated_data":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"Success": "Task has not completed.", "updated_data":serializer.data}, status=status.HTTP_200_OK)
        

class ManageLeaveView(APIView):
    permission_classes = [CanCraeteLeaveRequest]

    def post(self, request):
        request.data['empName'] = request.user.id
        serializer = ManageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class ApproveLeaveView(APIView):
    permission_classes = [CanViewLeaveRequestPermission]

    def patch(self,request, id):
        leave = ManageLeave.objects.get(pk=id)
        serializer = ApproveLeavetSerializer(leave, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if leave.approveLeave == True:
            response_data = {
                "Success": "Leave has been granted...",
                "updated_data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"Success": "Leave has been rejected!!!", "updated_data":serializer.data}, status=status.HTTP_200_OK)

class LeaveListView(ListAPIView):
    serializer_class = ListRequestSerializer
    queryset = ManageLeave.objects.all()
    filter_backends = [filters.DjangoFilterBackend] 
    filterset_class = LeaveFilter
    pagination_class = PageNumberPagination
    # permission_classes = [CanViewLeaveRequestPermission]  

class CreateSalaryView(APIView):
    permission_classes = [CanCreateSalary]

    def post(self, request):
        serializer = CrateSalarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)   
        serializer.save()
        return Response({"Success": "salary is created.", "updated_data":serializer.data}, status=status.HTTP_200_OK)
    
class SalaryPaymentView(APIView):
    permission_classes = [CanCreateSalary]

    def post(self, request):
        serializer = SalaryPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)