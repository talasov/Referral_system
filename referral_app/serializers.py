from rest_framework import serializers

from .models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    referred_users = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'invite_code', 'referred_users')

    def get_referred_users(self, obj):
        referred_users = CustomUser.objects.filter(referrers__referral_code=obj.invite_code)
        usernames = [user.username for user in referred_users]
        return usernames
