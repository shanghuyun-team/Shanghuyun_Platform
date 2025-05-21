from django.urls import path

from .views import RegisterPageView, LoginPageView, ProfilePageView


urlpatterns = [
    path('register/', RegisterPageView.as_view(), name='register'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('profile/', ProfilePageView.as_view(), name='profile'),
]