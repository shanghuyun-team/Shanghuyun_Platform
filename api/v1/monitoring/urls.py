from django.urls import path

from . import views

urlpatterns = [
    path("readings/", views.create_reading, name="monitoring_create_reading"),
]
