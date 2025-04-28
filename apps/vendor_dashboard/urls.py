from django.urls import path
from .views import home, add_product
urlpatterns = [
    path('', home, name='vendor_dashboard'),
    path('add_product/', add_product, name='add_product'),
]