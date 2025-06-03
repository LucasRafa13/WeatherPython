# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # Importa as views do seu app 'api'

# Cria um router para registar as ViewSets
router = DefaultRouter()
# Regista a WeatherRecordViewSet com o prefixo 'weather-records'
# Isso criará rotas como /api/weather-records/ (lista) e /api/weather-records/{pk}/ (detalhe)
router.register(
    r"weather-records", views.WeatherRecordViewSet, basename="weather-record"
)

urlpatterns = [
    # Inclui as rotas geradas pelo router (para WeatherRecordViewSet)
    path("", include(router.urls)),
    # A sua rota existente para o contexto de um único evento
    path(
        "contexto_evento/<str:event_id>/",
        views.event_context_api_view,
        name="event_context_api",
    ),
]
