from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
import random
import string
from django.utils import timezone
# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,username,email,password=None,**extra_fields):
        if not email:
            raise ValueError('User should have an Email Address')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,username,email,password=None):
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.is_admin=True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    username        =   models.CharField(max_length=50,unique=True)
    email           =   models.EmailField(unique=True)
    password        =   models.CharField(max_length=250)
    first_name      =   models.CharField(max_length=50)
    last_name       =   models.CharField(max_length=50)
    is_active       =   models.BooleanField(default=True)
    is_admin        =   models.BooleanField(default=False)
    is_doctor       =   models.BooleanField(default=False)
    is_staff        =   models.BooleanField(default=False)   
    allow_admin     =   models.BooleanField(default=False)
    is_verified     =   models.BooleanField(default=False)
    code_expires_at =   models.DateTimeField(blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    
    def generate_verification_code(self):
        self.verification_code = ''.join(random.choices(string.digits, k=6))
        self.code_expires_at = timezone.now() + timezone.timedelta(minutes=5) 
        self.save()
        
    objects = UserManager()
    
    def __str__(self):
        return self.username
    
    USERNAME_FIELD ='email'
    REQUIRED_FIELDS = ['username']  

    
    def has_perm(self,perm,obj=None):
        "This method is used to check whether the user has a specific permission"
        
        return self.is_admin
    def has_module_perms(self,app_label):
        "This method checks if the user has permissions for a particular app"
        return True
    
    @property
    def is_staff(self):
        "This property determines if the user is a member of staff and is used to control access to the Django admin site and other admin-specific functionality"
        return self.is_admin
    
class Doctor(models.Model):
    doctor=models.ForeignKey(User,on_delete=models.CASCADE)
    department=models.CharField(max_length=100)
    is_verified=models.BooleanField(default=False)
    profile_picture =   models.ImageField(upload_to='media')
    doctor_proof =   models.ImageField(upload_to='media')
    def __str__(self):
        return self.doctor.username