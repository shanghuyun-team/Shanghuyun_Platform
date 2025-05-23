from django.urls import path, include
from .views import ProfileRetrieveUpdateAPIView, social_choose

urlpatterns = [
    path('profile/', ProfileRetrieveUpdateAPIView.as_view(), name='api-profile'),
    path('social/choose/<int:pk>/', social_choose, name='social-choose')
    #path('user/', UserRetrieveUpdateAPIView.as_view(), name='api-user-detail'),
]