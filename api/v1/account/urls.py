from django.urls import path, include
from .views import RegisterAPIView, PasswordChangeAPIView, ProfileUpdateAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('password/change/', PasswordChangeAPIView.as_view(), name='password-change'),
    path('profile/', ProfileUpdateAPIView.as_view(), name='profile-detail'),
]