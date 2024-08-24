from django.shortcuts import render
from .models import User,Doctor
from .serializers import RegistraionSerializer,DoctorSerializer,UserSerializer,UsersSerialiazers,getEditDoctorSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


from django.conf import settings
from threading import Thread
from django.core.mail import EmailMessage
from django.utils import timezone

# send email
def send_email(subject, message, sender, recipient_list):
    email = EmailMessage(subject, message, sender, recipient_list)
    email.send()

# ////////////////////   TOKEN CUSTOMISATION  \\\\\\\\\\\\\\\\\\
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_doctor'] = user.is_doctor
        token['is_admin'] = user.is_admin
        token['allow_admin'] = user.allow_admin
        token['is_active'] = user.is_active
        return token
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class=MyTokenObtainPairSerializer
    
    
# /////////////////////// USER REGISTRATION \\\\\\\\\\\\\\\\\\\
class RegistrationUser(APIView):
    # def get(self,request):
    #     users=User.objects.all()
    #     serializer=UsersSerialiazers(users,many=True)
    #     return Response(serializer.data)
    
    def post(self, request):
        serializer = RegistraionSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            user = User.objects.create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                is_doctor=serializer.validated_data['is_doctor'],
                allow_admin=serializer.validated_data.get('allow_admin', False),
                is_active=False
            )
            if user.is_doctor:
                doctor = Doctor.objects.create(
                    doctor=user,
                    doctor_proof=serializer.validated_data['doctor_proof'],
                    department=serializer.validated_data['department'],
                    profile_picture=serializer.validated_data['profile_picture']
                )
                doctor.save()
        
            user.set_password(serializer.validated_data['password']) 
            user.save()
            
            # email verify
            user.generate_verification_code()
            print('verification code',user.verification_code)
            print('verification code expire',user.code_expires_at)
            print(timezone.now(),'time zone')
            subject='Email Verification Code'
            message=f'Your verification code is {user.verification_code}. This code will expire in 5 minutes.'
            email_thread = Thread(
                target=send_email, args=(subject, message, settings.EMAIL_HOST_USER, [user.email])
            )
            email_thread.start()
            
            
            return Response({'message': 'Registration Successful , Please check your email'}, status=status.HTTP_201_CREATED)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmail(APIView):
    def post(self,request):
        code=request.data.get('code')
        email=request.data.get('email')
        print('code',code)
        print('email',email)
        
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.verification_code == code and timezone.now() < user.code_expires_at:
            user.is_verified = True
            user.is_active = True
            user.verification_code = None  
            user.code_expires_at = None
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid or verifiction code expiredd.'}, status=status.HTTP_400_BAD_REQUEST)
         
    
# ADMIN SIDE DOCTOR VIEW AN DEDIT
class DoctorView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        print(request.user)
        doctor = Doctor.objects.all()

        if doctor.exists():
            serializer = DoctorSerializer(doctor, many=True)
            return Response({'doctors': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response( status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        try:
            doctor = Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    #  doctor get and edit
class DoctorEditGetView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        doctor=request.user
        # doctor='doctor3'
        # print(doctor)
        try:
            doctors=Doctor.objects.get(doctor__username=doctor)
            # print(doctors.department)
            serializer=getEditDoctorSerializer(doctors)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request):
        print('doctor data1',request.data)
        doctor = request.user
        # doctor='doctor3'
        print('user ',doctor)
        try:  
            doctor_instance = Doctor.objects.get(doctor__username=doctor)
            print(doctor_instance,'doctor instance')
        except Doctor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = getEditDoctorSerializer(doctor_instance, data=request.data, partial=True)
        # print(request.data,'request .dtataaaaa')
        if serializer.is_valid():
            serializer.save()
            # print('serializer data',serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
        #    user get and edit
class UserView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        user=request.user
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user=request.user
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdminView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        if users.exists():
            serializers = UsersSerialiazers(users, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            print(user,'user')
            action = request.data.get('action')
            if action == 'block':
                user.is_active = False
            elif action == 'unblock':
                user.is_active = True
                
            is_admin = request.data.get('is_admin', user.is_admin)
            user.is_admin = is_admin            
            if is_admin:
                user.allow_admin = False
            user.save()
            serializer = UsersSerialiazers(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
