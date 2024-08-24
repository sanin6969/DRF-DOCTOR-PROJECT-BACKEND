from rest_framework import serializers
from .models import Doctor,User
# from django.contrib.auth.hashers import make_password
import re
class UsersSerialiazers(serializers.ModelSerializer):
    class Meta:
        model=User
        exclude = ['password']     
           
class RegistraionSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(style={'input_type':'password'})
    doctor_proof=serializers.ImageField(required=False)
    profile_picture=serializers.ImageField(required=False)
    department=serializers.CharField(required=False)
    
    class Meta:
        model=User
        fields=['username','email',
                'password','confirm_password',
                'is_doctor','is_admin','doctor_proof',
                'profile_picture','department',
                'allow_admin','is_active']
        
    def validate(self,data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists, enter a new one'})   
             
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists, enter a new one'})
        
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'non_field_errors': ["Password doesn't match"]}) 
        
        if len(data['password']) < 8:
            raise serializers.ValidationError({'password': 'Password must be at least 8 characters long'})

        if not re.search(r'[A-Z]', data['password']):
            raise serializers.ValidationError({'password': 'Password must contain  one capital letter'})

        if not re.search(r'\d', data['password']):
            raise serializers.ValidationError({'password': 'Password must contain  one digit'})

        if not re.search(r'[@$!%*?&#]', data['password']):
            raise serializers.ValidationError({'password': 'Password must contain  one spcial character'})

        return data

# USER EDIT
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'is_doctor']

    def update(self, instance, validated_data):
        new_username = validated_data.get('username', instance.username)
        if User.objects.filter(username=new_username).exclude(id=instance.id).exists():
            raise serializers.ValidationError({'username': 'Username already exists, please enter a new one'})

        new_email = validated_data.get('email', instance.email)
        if User.objects.filter(email=new_email).exclude(id=instance.id).exists():
            raise serializers.ValidationError({'email': 'Email already exists, please enter a new one'})

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        instance.save()
        return instance
    
    
# doctor get and edit
class getEditDoctorSerializer(serializers.ModelSerializer):
    doctor=UsersSerialiazers()
    username=serializers.CharField(source='doctor.username')
    email=serializers.CharField(source='doctor.email')
    last_name=serializers.CharField(source='doctor.last_name')
    first_name=serializers.CharField(source='doctor.first_name')
    class Meta:
        model = Doctor
        fields = ['id', 'doctor', 'department', 'is_verified', 'profile_picture','doctor_proof','username','email','last_name','first_name']
        
        
    def update(self, instance, validated_data):
        print(validated_data,'validated data')
        # print(instance,'instance')
        doctor_data = validated_data.pop('doctor', None) 
        print(doctor_data,'doctordtaaa')
        if doctor_data:
            user_instance = instance.doctor
            
            new_username = doctor_data.get('username', user_instance.username)
            if User.objects.filter(username=new_username).exclude(id=user_instance.id).exists():
                raise serializers.ValidationError({'username': 'Username already exists, please enter a new one'})

            new_email = doctor_data.get('email', user_instance.email)
            if User.objects.filter(email=new_email).exclude(id=user_instance.id).exists():
                raise serializers.ValidationError({'email': 'Email already exists, please enter a new one'})
            
            print(user_instance.username,'username')
            user_instance.username = doctor_data.get('username', user_instance.username)
            print(user_instance.username,'updated username')
            
            user_instance.first_name = doctor_data.get('first_name', user_instance.first_name)
            user_instance.last_name = doctor_data.get('last_name', user_instance.last_name)
            user_instance.email = doctor_data.get('email', user_instance.email)
            print('helloo')
            user_instance.save()
            
        instance.department = validated_data.get('department', instance.department)
        instance.save()
        return instance
    
# ADMIN DOCTOR
class DoctorSerializer(serializers.ModelSerializer):
    doctor=UsersSerialiazers()
    class Meta:
        model = Doctor
        fields = ['id', 'doctor', 'department', 'is_verified', 'profile_picture','doctor_proof']

    
    def update(self, instance, validated_data):
        instance.is_verified = validated_data.get('is_verified', instance.is_verified)
        instance.save()
        return instance

    
    
    
    
    
    
    
    
    
    
