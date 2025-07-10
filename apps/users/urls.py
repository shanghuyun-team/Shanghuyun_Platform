from django.urls import path
from django.views.generic import TemplateView


from .views import ProfilePageView, PrivacyPolicyPageView, TermsOfServicePageView, privacy_policy


urlpatterns = [
    path('profile/', ProfilePageView.as_view(), name='profile'),
    path('privacy-policy/', PrivacyPolicyPageView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsOfServicePageView.as_view(), name='terms_of_service'),
    path("privacy/", privacy_policy, name="privacy_policy"),
    path(
        "privacy/", 
        TemplateView.as_view(template_name="users/privacy_policy.html"), 
        name="privacy_policy"
    ),
]