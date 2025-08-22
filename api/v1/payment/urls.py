from django.urls import path
from . import views

urlpatterns = [
    path("checkout/<int:order_id>/", views.ecpay_checkout, name="ecpay_checkout"),
    path('return/', views.ecpay_return, name='ecpay_return'),
]
