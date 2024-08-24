from django.contrib import admin
from .models import User,Doctor
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display=['id','username','email','is_active','is_doctor','is_admin']
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display=['id','department','is_verified','profile_picture','doctor_proof']
