from django.db import models
from django.utils.timezone import now

# Create your models here.

class CustomUser(models.Model):
    id = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=50)
    userEmail = models.EmailField()
    userPassword = models.CharField(max_length=50)
    userType = models.CharField(max_length=100, choices=(('Admin', 'Admin'),('Project-Manager', 'Project-Manager'),('Team-Leader', 'Team-Leader'),('Employee', 'Employee')))
    is_active = models.BooleanField(default=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.userType != 'Employee':
            self.is_active = None
        super().save(*args, **kwargs)   

class Project(models.Model):
    projectCreator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project_id = models.AutoField(primary_key=True)
    projectName = models.CharField(max_length=50)
    projectDescription = models.CharField(max_length=500)
    projectStartDate = models.DateField(default=now)

