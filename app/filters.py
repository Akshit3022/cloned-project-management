from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from app.models import *

class ProjectFilter(filters.FilterSet):
    project_name = filters.CharFilter(field_name='projectName', lookup_expr='icontains')
    employee_name = filters.CharFilter(field_name='projectCreator__name', lookup_expr='icontains')

    class Meta:
        model = Project
        fields = ['project_name', 'employee_name']     

class LeaveFilter(filters.FilterSet):
    empName = filters.CharFilter(field_name='empName__name', lookup_expr='icontains', label='Employee Name')
    
    class Meta:
        model = ManageLeave 
        fields = ['empName__name']