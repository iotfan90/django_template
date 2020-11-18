from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from api.serializers import UserSerializer, CreateUserSerializer, MyTokenObtainPairSerializer
from api.utils import TokenGenerator
from django.shortcuts import render
from mysite import settings
# import pyotp
# from twilio.rest import Client as TwillioClient
from random import randint


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class LoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request, *args, **kwargs):
        email = request.data['email']
        user = User.objects.get(email=email)

        if not user:
            return Response(dict(detail="Please register"), status=404)
        else:
            phone_verification = user.is_phone_verified
            # if user.is_active is False:
            #     return Response(dict(detail="Please verify your email address"), status=401)
            if phone_verification is False:
                return Response(dict(detail="Please verify your phone number"), status=201)
            if user.is_active:
                MyTokenObtainPairView()


class UserInfoAPIView(generics.RetrieveAPIView, generics.UpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = request.user
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.email = request.data['email']
        user.save()
        user.phone_number = request.data['phone_number']
        phone_verification_url = '%s/login/phone_verification?uid=%s&token=%s' % (request.build_absolute_uri('/')[:-1],
                                                                                  urlsafe_base64_encode(force_bytes(user.pk)),
                                                                                  TokenGenerator().make_token(user))
        user.save()
        try:
            name = user.first_name + ' ' + user.last_name
            message = render_to_string('emails/phone_verification.html', {
                'name': name,
                'phone_verification_url': phone_verification_url,
            })
            email = EmailMessage(
                'Phone verification', message, to=[user.email]
            )
            email.send()
        except Exception:
            pass
        return Response(data=self.get_serializer(user).data)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# class UserSingUpView(APIView):
#     permission_classes = (permissions.AllowAny,)
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         serializer = CreateUserSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response({
#                 'message': 'Some fields are missing',
#                 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         data = serializer.validated_data
#         try:
#             num = randint(100000, 999999)
#             user = User.objects.create(email=data['email'], first_name=data['first_name'], username=data['email'],
#                                        last_name=data['last_name'], is_active=False, email_verification_code=num)
#             user.set_password(data['password'])
#             user.save()
#         except IntegrityError as e:
#             return Response({
#                 'message': 'Email already exists.',
#                 'errors': {'email': 'Email already exists.'}
#                  }, status=status.HTTP_400_BAD_REQUEST)
#
#         # email_verification_url = '%s/login/email_verification?uid=%s&token=%s' % (request.build_absolute_uri('/')[:-1],
#         #                                                                           urlsafe_base64_encode(force_bytes(user.pk)),
#         #                                                                           TokenGenerator().make_token(user))
#
#         try:
#             name = user.first_name + ' ' + user.last_name
#             message = render_to_string('emails/email_verification.html', {
#                 'name': name,
#                 'email_verification_code': num,
#             })
#             email = EmailMessage(
#                 'Email verification', message, to=[user.email]
#             )
#             email.send()
#         except Exception:
#             pass
#
#         return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)


# class SendSmsCodeView(APIView):
#     permission_classes = (permissions.AllowAny,)
#
#     @staticmethod
#     def post(request, *args, **kwargs):
#         try:
#             email = request.data['email']
#             user = User.objects.get(email=email)
#             if user is None:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#             try:
#                 user.phone_number = request.data['phone_number']
#                 key = pyotp.random_base32()
#                 time_otp = pyotp.TOTP(key, interval=300)
#                 time_otp = time_otp.now()
#                 user.otp = time_otp
#                 user.save()
#                 user_phone_number = user.phone_number  # Must start with a plus '+'
#                 account_sid = settings.TWILIO_ACCOUNT_SID
#                 auth_token = settings.TWILIO_AUTH_TOKEN
#                 twilio_phone = settings.TWILIO_PHONE
#                 client = TwillioClient(account_sid, auth_token)
#                 client.messages.create(
#                     body="Your verification code is " + time_otp,
#                     from_=twilio_phone,
#                     to=user_phone_number
#                 )
#             except IntegrityError:
#                 return Response({
#                     'phone_number': 'Phone number already exists.',
#                     'errors': {'phone_number': 'Phone number already exists.'}
#                 }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception:
#             pass
#         return Response(status=status.HTTP_200_OK)


# class VerifyPhoneView(APIView):
#     permission_classes = (permissions.AllowAny,)
#
#     @staticmethod
#     def post(request):
#         code = request.data['code']
#         user = User.objects.get(otp=code)
#
#         if user:
#             user.is_active = True
#             user.is_phone_verified = True
#             user.save()
#             return Response(dict(detail="Phone number verified successfully"), status=201)
#         return Response(dict(detail='The provided code did not match or has expired'), status=200)


class VerifyEmailView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request):
        email = request.data['email']
        code = request.data['code']
        user = User.objects.get(email=email)

        if user.email_verification_code == code:
            user.is_active = True
            user.save()
            return Response(dict(detail="Email address verified successfully"), status=201)
        return Response(dict(detail='The provided email did not match'), status=200)


class ResendEmailView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request):
        email = request.data['email']
        user = User.objects.get(email=email)

        if user:
            num = randint(100000, 999999)
            user.email_verification_code = num
            user.save()

            try:
                name = user.first_name + ' ' + user.last_name
                message = render_to_string('emails/email_verification.html', {
                    'name': name,
                    'email_verification_code': num,
                })
                email = EmailMessage(
                    'Email Verification', message, to=[user.email]
                )
                email.send()
            except Exception:
                pass
            return Response(dict(detail="Resend email verification code done successfully."), status=201)
        return Response(dict(detail='The provided email did not match'), status=200)


class ResendPhoneView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request):
        phone_number = request.data['phone_number']
        user = User.objects.get(phone_number=phone_number)

        if user:
            num = randint(100000, 999999)
            user.email_verification_code = num
            user.save()

            try:
                name = user.first_name + ' ' + user.last_name
                message = render_to_string('emails/email_verification.html', {
                    'name': name,
                    'email_verification_code': num,
                })
                email = EmailMessage(
                    'Email Verification', message, to=[user.email]
                )
                email.send()
            except Exception:
                pass
            return Response(dict(detail="Resend email verification code done successfully."), status=201)
        return Response(dict(detail='The provided email did not match'), status=200)


class ResetPasswordAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request, *args, **kwargs):
        email = request.data['email']
        user = User.objects.get(username=email)
        if user:
            password_reset_url = '%s/login/reset_password?uid=%s&token=%s' % (request.build_absolute_uri('/')[:-1],
                                                                             urlsafe_base64_encode(force_bytes(user.pk)),
                                                                             TokenGenerator().make_token(user))

            try:
                name = user.first_name + ' ' + user.last_name
                message = render_to_string('emails/reset_password.html', {
                    'name': name,
                    'password_set_url': password_reset_url,
                })
                email = EmailMessage(
                    'Please reset your password.', message, to=[user.email]
                )
                email.send()
            except Exception:
                pass
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CreatePasswordAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(request.data['uid']))
            user = User.objects.get(pk=uid)
            if user is None or not TokenGenerator().check_token(user, request.data['token']):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            try:
                user.set_password(request.data['password'])
                user.is_active = True
                user.save()
            except IntegrityError:
                return Response({
                    'password': 'Password already exists.',
                    'errors': {'password': 'Password already exists.'}
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


def index(request):

    return render(request, 'home.html')


def home(request):

    return render(request, 'home.html')


def repeat_play2_outcome(request):

    return render(request, 'repeat_play_2_outcome.html')

