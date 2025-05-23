from django.urls import path, include
from .views import ProfileRetrieveUpdateAPIView, UserRetrieveUpdateAPIView

urlpatterns = [
    path('profile/', ProfileRetrieveUpdateAPIView.as_view(), name='api-profile'),
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='api-user-detail'),
]