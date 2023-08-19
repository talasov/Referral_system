from django.urls import path
from .views import PhoneNumberAuthorizationView, VerifyAuthCodeView, UserProfileView, AssignReferralCodeView
from .web_views import authorization_page, verification_page, assign_referral_code, user_profile


urlpatterns = [
    path('api/authorize/', PhoneNumberAuthorizationView.as_view(), name='authorize'),
    path('api/verify/', VerifyAuthCodeView.as_view(), name='verify'),
    path('api/assign-referral-code/', AssignReferralCodeView.as_view(), name='assign-referral-code'),
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),


    path('authorization/', authorization_page, name='authorization'),
    path('verification/', verification_page, name='verify'),
    path('assign-referral-code/', assign_referral_code, name='assign-referral-code'),
    path('profile/', user_profile, name='user_profile'),
]
