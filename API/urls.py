from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
urlpatterns = [
    path('register/',RegistrationUser.as_view(),name='register'),
    path('doctorgetedit/',DoctorEditGetView.as_view(),name='doctorgetedit'), # for doctr editng and updating
    path('doctor/',DoctorView.as_view(),name='doctor'), # to show all doctrs in admin side
    path('doctor/<int:pk>/', DoctorView.as_view(), name='doctor-detail'), # to update doctor in admin side verify an dblock
    path('admin/',AdminView.as_view(),name='admin'), 
    path('admin/<int:pk>/',AdminView.as_view(),name='admin'), 
    path('verifyemail/',VerifyEmail().as_view(),name='verifyemail'), # for email verification
    path('user/',UserView.as_view(),name='user'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]