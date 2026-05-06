from django.urls import path

from . import views

app_name = "monitoring"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("sensors/", views.sensor_list, name="sensor_list"),
    path("sensors/create/", views.sensor_create, name="sensor_create"),
    path("sensors/<int:pk>/", views.sensor_detail, name="sensor_detail"),
    path("sensors/<int:pk>/edit/", views.sensor_edit, name="sensor_edit"),
    path("sensors/<int:pk>/delete/", views.sensor_delete, name="sensor_delete"),
    path("sensors/<int:pk>/data/", views.sensor_data_api, name="sensor_data_api"),
    # AI 即時建議
    path("ai-recommendation/", views.ai_recommendation, name="ai_recommendation"),
    path("sensors/<int:pk>/ai-recommendation/", views.ai_sensor_recommendation, name="ai_sensor_recommendation"),
]
