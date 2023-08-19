import random
import string

from .models import CustomUser


def get_or_create_user(phone_number):
    """ Проверка корректности номера """
    try:
        return CustomUser.objects.get(phone_number=phone_number)
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create_user(phone_number=phone_number)
        user.is_verified = True
        user.save()
        return user


def generate_invite_code(user):
    """ Создание invite_code """
    if not user.invite_code:
        invite_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        user.invite_code = invite_code
        user.save()
    return user.invite_code
