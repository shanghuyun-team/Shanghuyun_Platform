from django.urls import path
from apps.sale.views import homePage

urlpatterns = [
    path('', homePage, name='home'),
]
