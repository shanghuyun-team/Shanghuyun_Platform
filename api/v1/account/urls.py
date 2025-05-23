from django.urls import path, include
from .views import ProfileRetrieveUpdateAPIView, UserRetrieveUpdateAPIView, EmailVerifiedAPIView

urlpatterns = [
    path('profile/', ProfileRetrieveUpdateAPIView.as_view(), name='api-profile'),
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='api-user-detail'),
    path(
        'user/<int:pk>/email-verified/',
        EmailVerifiedAPIView.as_view(),
        name='api-user-email-verified'
    ),
]