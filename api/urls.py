from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    # path('auth/register', views.UserSingUpView.as_view(), name='register'),
    # path('auth/send_sms_code', views.SendSmsCodeView.as_view(), name='sms_code'),
    # path('auth/verify_phone', views.VerifyPhoneView.as_view(), name='verify_phone'),
    path('auth/verify_email', views.VerifyEmailView.as_view(), name='verify_email'),
    path('auth/resend_email', views.ResendEmailView.as_view(), name='resend_email'),
    path('auth/resend_phone_number', views.ResendPhoneView.as_view(), name='resend_phone_number'),
    path('auth/user/reset_password', views.ResetPasswordAPIView.as_view(), name='reset_password'),
    path('auth/login/create_password', views.CreatePasswordAPIView.as_view(), name='create_password'),
    # path('auth/login', views.LoginAPIView.as_view(), name='login'),
    path('auth/login', views.MyTokenObtainPairView.as_view(), name='login'),
    path('auth/token-refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user', views.UserInfoAPIView.as_view(), name='user_info'),
]

urlpatterns += router.urls

