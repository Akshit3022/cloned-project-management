from rest_framework import permissions

class CanCreateProjectPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_type = getattr(request.user, 'userType', None)
        print("userType: ",user_type)
        return user_type in ['Admin', 'Project-Manager', 'Team-Leader']