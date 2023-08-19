import random
import string
import time

import phonenumbers
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Referral
from .serializers import UserProfileSerializer


class PhoneNumberAuthorizationView(APIView):
    """ Представление для отправки кода авторизации на номер телефона """

    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({'error': 'Требуется номер телефона'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed_phone = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_phone):
                return Response({'error': 'Некорректный номер телефона'}, status=status.HTTP_400_BAD_REQUEST)
        except phonenumbers.NumberParseException:
            return Response({'error': 'Некорректный номер телефона'}, status=status.HTTP_400_BAD_REQUEST)

        auth_code = ''.join(random.choice(string.digits) for _ in range(4))
        auth_code_created_at = timezone.now()

        # Эмулируем задержку в 2 секунды
        time.sleep(2)

        cache_key = f'auth_code_{phone_number}'
        cache.set(cache_key, {'code': auth_code, 'phone_number': phone_number, 'created_at': auth_code_created_at},
                  timeout=3 * 60)

        return Response({'auth_code': auth_code}, status=status.HTTP_200_OK)


class VerifyAuthCodeView(APIView):
    """ Верефикация пользователя по коду (auth_code) ,
        Присвоение новому пользователю invite_code """

    def post(self, request):
        phone_number = request.data.get('phone_number')
        auth_code = request.data.get('auth_code')

        if not phone_number or not auth_code:
            return Response({'error': 'Требуется номер телефона и код авторизации'}, status=status.HTTP_400_BAD_REQUEST)

        if not self.validate_phone_number(phone_number):
            return Response({'error': 'Некорректный номер телефона'}, status=status.HTTP_400_BAD_REQUEST)

        cached_data = cache.get(f'auth_code_{phone_number}')

        if not cached_data or cached_data['code'] != auth_code or cached_data[
            'created_at'] < timezone.now() - timezone.timedelta(minutes=3):
            return Response({'error': 'Неверный код авторизации или время истекло'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.get_or_create_user(phone_number)
        invite_code = self.generate_invite_code(user)
        token = self.generate_token(user)

        return Response({
            'message': 'Пользователь успешно авторизован и инвайт-код присвоен',
            'invite_code': invite_code,
            'token': token,
        }, status=status.HTTP_200_OK)

    def validate_phone_number(self, phone_number):
        """ Проверка ввода номера"""
        try:
            parsed_phone = phonenumbers.parse(phone_number, None)
            return phonenumbers.is_valid_number(parsed_phone)
        except phonenumbers.NumberParseException:
            return False

    def get_or_create_user(self, phone_number):
        """ Создание нового пользователя """
        try:
            return CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create_user(phone_number=phone_number)
            user.is_verified = True
            user.save()
            return user

    def generate_invite_code(self, user):
        """ Создание invite_code"""
        if not user.invite_code:
            invite_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
            user.invite_code = invite_code
            user.save()
        return user.invite_code

    def generate_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        serializer = UserProfileSerializer(user, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignReferralCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        referral_code = request.data.get('referral_code')

        if not referral_code:
            return Response({'error': 'Требуется указать referral_code'}, status=status.HTTP_400_BAD_REQUEST)

        if Referral.objects.filter(referred_user=user).exists():
            return Response({'error': 'У вас уже есть реферальный код'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            referred_by_user = CustomUser.objects.get(invite_code=referral_code)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Указанный referral code не найден'}, status=status.HTTP_400_BAD_REQUEST)

        if referred_by_user == user:
            return Response({'error': 'Вы не можете использовать свой invite code как referral code'},
                            status=status.HTTP_400_BAD_REQUEST)

        Referral.objects.create(referrer=referred_by_user, referred_user=user, referral_code=referral_code)

        return Response({'message': 'Реферальный код успешно присвоен'}, status=status.HTTP_201_CREATED)


