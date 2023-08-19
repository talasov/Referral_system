from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """ Менеджер User модели """
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Необходимо указать номер телефона')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.username = phone_number  # Присваиваем username значение phone_number
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)
