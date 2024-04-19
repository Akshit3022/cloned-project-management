from django.urls import path
from app.views import *
from app import views

urlpatterns = [
    # register/login
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user-profile/', CustomUserProfileView.as_view(), name='user-profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # password management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('send-password/', SendResetPasswordEmaiView.as_view(), name='send-password'),
    path('reset-password/<user_id>/<token>/', CustomUserResetPasswordView.as_view(), name='reset-password'),
    # project management
    path('project-create/', projectCreateView.as_view(), name='project-create'),
    path('project/', ProjectListView.as_view(), name='project-list'),
    path('project/<int:id>/', ProjectCRUDView.as_view(), name='project-update-delete'),
    # allocation
    path('project-allocation/', ProjectAllocationView.as_view(), name='project-allocation'),
    path('employee-allocation-list/', EmployeeAllocationListView.as_view(), name='employee-allocation-list'),
    # task management
    path('task-status/<int:id>/', TaskStatusView.as_view(), name='task-status'),
    # leave management
    path('request-leave/', ManageLeaveView.as_view(), name='request-leave'),
    path('leave-list/', LeaveListView.as_view(), name='leave-list'),
    path('approve-leave/<int:id>/', ApproveLeaveView.as_view(), name='approve-leave'),
    # salary management
    # path('pay-salary/', SalaryPaymentView.as_view(), name='pay-salary'),
    # path('payment-details/', views.SendPaymentDetailsView.as_view(), name='payment-details'),
    path('pay-salary/', PaySalaryView.as_view(), name='pay-salary'),
]       