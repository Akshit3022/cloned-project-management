from datetime import datetime, timedelta
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


# import stripe
import requests


#---------------------------- Regestraion/Login ---------------------------- start


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


#---------------------------- Regestraion/Login ---------------------------- end


#---------------------------- Password Management ---------------------------- start


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
        

#---------------------------- Password Management ---------------------------- end
        

#---------------------------- Project Management ---------------------------- start


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


#---------------------------- Password Management ---------------------------- end


#---------------------------- Allocation ---------------------------- start


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
    

#---------------------------- Allocation ---------------------------- end


#---------------------------- Task Management ---------------------------- start
    

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
        else:
            return Response({"Pending": "Task has not completed.", "updated_data":serializer.data}, status=status.HTTP_200_OK)
        

#---------------------------- Task Management ---------------------------- end


#---------------------------- Leave Management ---------------------------- start


class ManageLeaveView(APIView):
    permission_classes = [CanCraeteLeaveRequest]

    # def post(self, request):
    #     request.data['empName'] = request.user.id
    #     serializer = ManageRequestSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request):
        start_date = request.data.get('leaveStartDate')
        end_date = request.data.get('leaveEndDate')
        
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        print("start_date", start_date)
        print("end_date", end_date)
        
        # Calculate total leave days
        total_leave_days = (end_date - start_date).days + 1

        print("total_leave_days", total_leave_days)

        # Assign total_leave_days to request data
        request.data['leave_days'] = total_leave_days
        request.data['empName'] = request.user.id
        
        # Serialize and save leave request
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

#---------------------------- Leave Management ---------------------------- end


#---------------------------- Salary Management ---------------------------- start


# stripe.api_key = settings.STRIPE_SECRET_KEY

# class SendPaymentDetailsView(TemplateView):
#     template_name = 'payment.html'

#     def message(request):
#         if request.method == 'POST':
#             payment_method = stripe.PaymentMethod.create(
#                 type="card",
#                 card={"token": request.POST['stripeToken']}
#             )

#             payment_intent = stripe.PaymentIntent.create(
#                 amount=25000,
#                 currency='inr',
#                 description='stripe payment intent',
#                 payment_method=payment_method.id,
#                 confirm=True,
#                 return_url='http://127.0.0.1:8000/api/payment-details/'
#         ) 

# class SalaryPaymentView(APIView):
#     # permission_classes = [CanCreateSalary]
#     parser_classes = [JSONParser]
#     print("CNCNCN")
#     def post(self, request):
#         data = request.data
#         print("data", data)
#         payment_method = data.get('payment_method')
#         print("payment_method", payment_method)

#         amount_str = data.get('amount', '0')
#         amount = max(int(amount_str) if amount_str else 0, 50)

#         payment_intent = stripe.PaymentIntent.create(
#             amount=amount,
#             currency='inr',
#             description='Salary payment',
#             payment_method=payment_method,
#             confirm=True,
#             return_url='http://127.0.0.1:8000/api/pay-salary/'
#         )

#         serializer = SalaryPaymentSerializer(data={'user': request.user.id, 'amount': amount, 'payment_method': payment_method})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({'payment_intent_id': payment_intent.id}, status=status.HTTP_200_OK)
    

from django.db.models import Sum

class PaySalaryView(APIView):
    permission_classes = [CanCreateSalary]

    def post(self, request):
        user_id = request.data.get('user')
        print("user",user_id)
        provided_salary_amount = float(request.data.get('amount'))
        emp = ManageLeave.objects.filter(empName=user_id)
        print("emp",emp)
        
        # Get the total approved leave days for the user
        # total_leave_days = user.leaves_requested.filter(approveLeave=True).aggregate(total_leave_days=models.Sum('leaveDays'))['total_leave_days'] or 0
        total_leave_days = ManageLeave.objects.filter(empName=user_id, approveLeave=True).aggregate(total_leave_days=Sum('leave_days'))['total_leave_days']
        print("total_leave_days", total_leave_days)  
        # Calculate the remaining working days after deducting leave days
        remaining_working_days = 21 - total_leave_days
        
        # Calculate the total salary percentage based on remaining working days
        total_salary_percentage = (remaining_working_days / 21) * 100

        # Get the user's default salary percentage
        default_salary_percentage = 100
        
        # Determine the actual salary percentage to be used
        actual_salary_percentage = min(default_salary_percentage, total_salary_percentage)
        
        # Calculate the salary amount based on the actual salary percentage
        salary_amount = (actual_salary_percentage / 100) * provided_salary_amount
        amount = int(salary_amount)
        # Save the salary payment information
        serializer = PaySalarySerializer(data={'user': user_id, 'amount': amount, 'payment_method': request.data.get('payment_method')})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    # def post(self, request):
    #     user = request.data.get('user')
    #     leave_days = CustomUser.objects.filter(approveLeave=True).aggregate(total_leave_days=models.Sum('leave_days'))['total_leave_days'] or 0
    #     total_salary_percentage = 100 - (leave_days / 21 * 100)  

    #     actual_salary_percentage = min(user.default_salary_percentage, total_salary_percentage)
    #     salary_amount = (actual_salary_percentage / 100) * user.base_salary 

    #     serializer = PaySalarySerializer(data={'user': user.id, 'amount': salary_amount, 'payment_method': request.data.get('payment_method')})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    # def post(self, request):
    #     user = request.user
    #     leave_days = CustomUser.objects.filter(approveLeave=True).aggregate(total_leave_days=models.Sum('leave_days'))['total_leave_days'] or 0
    #     total_salary_percentage = 100 - (leave_days / 21 * 100)  

    #     actual_salary_percentage = min(user.default_salary_percentage, total_salary_percentage)
    #     salary_amount = (actual_salary_percentage / 100) * user.base_salary 

    #     # Create an order in PayPal
    #     paypal_url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders'
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Authorization': 'Bearer YOUR_PAYPAL_ACCESS_TOKEN'
    #     }
    #     data = {
    #         'intent': 'CAPTURE',
    #         'purchase_units': [{
    #             'amount': {
    #                 'currency_code': 'USD',
    #                 'value': str(salary_amount)
    #             }
    #         }]
    #     }

    #     response = requests.post(paypal_url, json=data, headers=headers)
    #     if response.status_code != 201:
    #         return Response({"message": "Failed to create PayPal order"}, status=status.HTTP_400_BAD_REQUEST)

    #     # Extract PayPal order ID from the response
    #     paypal_order_id = response.json()['id']

    #     # Save the PayPal order ID along with other payment details
    #     serializer = PaySalarySerializer(data={'user': user.id, 'amount': salary_amount, 'payment_method': 'PayPal', 'paypal_order_id': paypal_order_id})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    #     # Return the PayPal order ID in the response
    #     return Response({"paypal_order_id": paypal_order_id}, status=status.HTTP_201_CREATED)

    
#---------------------------- Salary Management ---------------------------- end