# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home_view, name="home"),
    path(
        "query-weather/", views.query_weather_data, name="query_weather"
    ),  # Para a consulta inicial (retorna JSON)
    path(
        "save-weather-data/", views.save_weather_data, name="save_weather_data"
    ),  # Para salvar no DB (via POST)
    path("api/", include("api.urls")),
]
