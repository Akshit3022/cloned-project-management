from django.contrib import admin
from app.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

class UserModelAdmin(BaseUserAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["id", "email", "name", "userType", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ('User Credential', {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name", "userType"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "userType", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []


# Now register the new UserAdmin...
    
admin.site.register(CustomUser, UserModelAdmin)

class ProjectModelAdmin(admin.ModelAdmin):
    list_display = ["project_id","projectCreator", "projectName", "projectStartDate"]
admin.site.register(Project, ProjectModelAdmin)