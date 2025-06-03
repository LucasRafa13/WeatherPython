# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views  # Importa as views do seu myproject/views.py

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home_view, name="home"),  # Rota raiz para o formulário
    path(
        "query-weather/", views.query_weather_data, name="query_weather"
    ),  # <-- ESTA ROTA É CRUCIAL
    path("api/", include("api.urls")),  # Inclui as URLs do seu app 'api'
]
