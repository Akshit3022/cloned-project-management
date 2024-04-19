from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.


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
    typeChoices = [
        ('Admin', 'Admin'),
        ('Project_Manager', 'Project_Manager'),
        ('Team_Leader', 'Team_Leader'),
        ('Employee', 'Employee'),
    ]
    userType = models.CharField(max_length=100, choices=typeChoices) 
    allocation_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    default_salary_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100)
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
    projectCreator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='created_by')
    assignToPM = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='assign_to_pm')
    project_id = models.AutoField(primary_key=True)
    projectName = models.CharField(max_length=50)
    projectDescription = models.CharField(max_length=500)
    projectStartDate = models.DateField(default=now)
    projectEndDate = models.DateField(null=True)
    todoChoices = [
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]
    projectStatus = models.CharField(max_length=100, choices=todoChoices) 


class ProjectAllocation(models.Model):
    emp_allocation = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  
    allocation_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    taskName = models.CharField(max_length=100, null=True)
    taskDescription = models.CharField(max_length=500, null=True)
    taskStartDate = models.DateField(null=True)
    taskEndDate = models.DateField(null=True)
    taskStatus = models.BooleanField(default=False, null=True)

class ManageLeave(models.Model):
    empName = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='leaves_requested')
    leaveStartDate = models.DateField()
    leaveEndDate = models.DateField()
    typeOfLeave = [
        ('half-day', 'half-day'),
        ('full-day', 'full-day'),
    ]
    leaveType = models.CharField(max_length=100, choices=typeOfLeave ,default='full-day') 
    leaveReason = models.CharField(max_length=500)
    notifyTo = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leaves_notified')
    approveLeave = models.BooleanField(default=False, null=True)
    leave_days = models.IntegerField(default=0)

    
class SalaryPayment(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=now)
    payment_method = models.CharField(max_length=100)   

