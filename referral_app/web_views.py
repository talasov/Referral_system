import random
import string
import time

import phonenumbers
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render
from django.utils import timezone

from .utils import get_or_create_user, generate_invite_code


def authorization_page(request):
    """ Авторизация """

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
    """ Верефикация """
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

                # Вход пользователя
                login(request, user)

    context = {
        'invite_code': invite_code,
        'phone_number': phone_number,
    }

    return render(request, 'referral_app/verification.html', context)


@login_required
def profile_page(request):
    """ Профиль пользователя """

    user = request.user

    context = {
        'user': user,
    }

    return render(request, 'referral_app/user_profile.html', context)
