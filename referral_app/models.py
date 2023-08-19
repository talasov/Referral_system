from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from .managers import CustomUserManager


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
