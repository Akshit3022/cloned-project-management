from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.

# class CustomUser(models.Model):
#     id = models.AutoField(primary_key=True)
#     userName = models.CharField(max_length=50)
#     userEmail = models.EmailField()
#     userPassword = models.CharField(max_length=50)
#     userType = models.CharField(max_length=100, choices=(('Admin', 'Admin'),('Project-Manager', 'Project-Manager'),('Team-Leader', 'Team-Leader'),('Employee', 'Employee')))
#     is_active = models.BooleanField(default=True, null=True, blank=True)

#     def save(self, *args, **kwargs):
#         if self.userType != 'Employee':
#             self.is_active = None
#         super().save(*args, **kwargs)   



class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, userType, password=None, confirmPass=None, is_active=True):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,      
            userType=userType,
            is_active=is_active
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, userType, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            userType=userType
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=50)
    userType = models.CharField(max_length=100, choices=(('Admin', 'Admin'),('Project-Manager', 'Project-Manager'),('Team-Leader', 'Team-Leader'),('Employee', 'Employee'))) 
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)   

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "userType"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

class Project(models.Model):
    projectCreator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project_id = models.AutoField(primary_key=True)
    projectName = models.CharField(max_length=50)
    projectDescription = models.CharField(max_length=500)
    projectStartDate = models.DateField(default=now().date)
    projectEndDate = models.DateField(null=True)
    toDo = models.CharField(max_length=100, choices=(('In progress', 'In progress'),('Completed', 'Completed'))) 
