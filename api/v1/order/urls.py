# api/v1/order/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_order, name="create_order"),
    path('result/', views.order_result, name='order_result'),
    path('history/', views.order_history, name='order_history'),
]
