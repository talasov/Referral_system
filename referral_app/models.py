from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
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


class CustomUser(AbstractUser):
    groups = models.ManyToManyField(Group, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions')
    phone_number = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(max_length=6, null=True, blank=True)
    activated_invite_code = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'


class Referral(models.Model):
    referrer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referred_users')
    referred_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrers')
    referral_code = models.CharField(max_length=6)

    def __str__(self):
        return f"{self.referrer.username} -> {self.referred_user.username}"
