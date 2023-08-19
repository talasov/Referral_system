import random
import string
import time

import phonenumbers
from django.core.cache import cache
from django.shortcuts import render
from django.utils import timezone

from django.urls import reverse

from .models import CustomUser, Referral
from django.contrib.auth.decorators import login_required


def authorization_page(request):
    auth_code = None
    phone_number = None

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        if phone_number:
            parsed_phone = phonenumbers.parse(phone_number, None)
            if phonenumbers.is_valid_number(parsed_phone):
                auth_code = ''.join(random.choice(string.digits) for _ in range(4))
                auth_code_created_at = timezone.now()

                # Эмулируем задержку в 2 секунды
                time.sleep(2)

                cache_key = f'auth_code_{phone_number}'
                cache.set(cache_key,
                          {'code': auth_code, 'phone_number': phone_number, 'created_at': auth_code_created_at},
                          timeout=3 * 60)

    context = {
        'auth_code': auth_code,
        'phone_number': phone_number,
    }

    return render(request, 'referral_app/authorization.html', context)


def verification_page(request):
    invite_code = None
    phone_number = request.POST.get('phone_number')
    auth_code = request.POST.get('auth_code')

    if phone_number and auth_code:
        parsed_phone = phonenumbers.parse(phone_number, None)
        if phonenumbers.is_valid_number(parsed_phone):
            cached_data = cache.get(f'auth_code_{phone_number}')

            if cached_data and cached_data['code'] == auth_code and cached_data[
                'created_at'] >= timezone.now() - timezone.timedelta(minutes=3):
                user = get_or_create_user(phone_number)
                invite_code = generate_invite_code(user)

                if invite_code:
                    # Перенаправляем на профиль пользователя с помощью URL-имени
                    return redirect(reverse('user_profile'))

    context = {
        'invite_code': invite_code,
        'phone_number': phone_number,
    }

    return render(request, 'referral_app/verification.html', context)


def get_or_create_user(phone_number):
    try:
        return CustomUser.objects.get(phone_number=phone_number)
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create_user(phone_number=phone_number)
        user.is_verified = True
        user.save()
        return user


def generate_invite_code(user):
    if not user.invite_code:
        invite_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        user.invite_code = invite_code
        user.save()
    return user.invite_code


from django.shortcuts import redirect
@login_required
def assign_referral_code(request):
    success_message = None

    if request.method == 'POST':
        user = request.user
        referral_code = request.POST.get('referral_code')

        if not referral_code:
            error_message = 'Требуется указать инвайт-код'
        else:
            referred_by_user = CustomUser.objects.filter(invite_code=referral_code).first()

            if not referred_by_user:
                error_message = 'Указанный инвайт-код не найден'
            elif Referral.objects.filter(referred_user=user).exists():
                error_message = 'У вас уже есть реферальный код'
            elif referred_by_user == user:
                error_message = 'Вы не можете использовать свой инвайт-код как реферальный'
            else:
                Referral.objects.create(referrer=referred_by_user, referred_user=user, referral_code=referral_code)
                success_message = 'Реферальный код успешно присвоен'

    context = {
        'success_message': success_message,
    }

    return render(request, 'referral_app/referral_assignment.html', context)




def user_profile(request):
    user = request.user
    return render(request, 'referral_app/user_profile.html', {'user': user})
