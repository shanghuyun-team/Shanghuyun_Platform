from django.urls import path

from .views import ProfilePageView, PrivacyPolicyPageView, TermsOfServicePageView


urlpatterns = [
    path('profile/', ProfilePageView.as_view(), name='profile'),
    path('privacy-policy/', PrivacyPolicyPageView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsOfServicePageView.as_view(), name='terms_of_service'),
]