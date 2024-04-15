from rest_framework import permissions
    
class CanCreateProjectPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print("Permission")
        user_type = getattr(request.user, 'userType', None)
        print("userType: ",user_type)
        return user_type in ['Admin', 'Project_Manager', 'Team_Leader']
    

class CanAllocateProject(permissions.BasePermission):
    def has_permission(self, request, view):
        user_type = getattr(request.user, 'userType', None)
        print("userType: ",user_type)
        return user_type == 'Project_Manager'
    
class CanChangeTaskStatus(permissions.BasePermission):
    def has_permission(self, request, view):
        user_type = getattr(request.user, 'userType', None)
        print("userType: ",user_type)
        return user_type == 'Employee'