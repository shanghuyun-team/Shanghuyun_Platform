from django.urls import path, include
from .views import ProfileRetrieveUpdateAPIView

urlpatterns = [
    path('profile/', ProfileRetrieveUpdateAPIView.as_view(), name='api-profile'),
]