# api/urls.py
from django.urls import path
from .views import WeatherRecordListCreateAPI

urlpatterns = [
    # A rota padrão da API (ex: /api/) será tratada por WeatherRecordListCreateAPI
    path("", WeatherRecordListCreateAPI.as_view(), name="weather-records-list-create"),
    # Se quiser uma rota para detalhes/PUT/DELETE de um item específico, seria outro path e outra view
    # path('<int:pk>/', WeatherRecordDetailAPI.as_view(), name='weather-record-detail'),
]
