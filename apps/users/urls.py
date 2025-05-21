from django.urls import path

from .views import RegisterPageView, LoginPageView


urlpatterns = [
    path('register/', RegisterPageView.as_view(), name='register'),
    path('login/', LoginPageView.as_view(), name='login'),
]