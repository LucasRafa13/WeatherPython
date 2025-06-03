# api/serializers.py
from rest_framework import serializers
from weather_data.models import WeatherRecord  # Importa o modelo WeatherRecord


class WeatherRecordSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo WeatherRecord.
    Define como os objetos WeatherRecord são convertidos para/de representações JSON.
    """

    class Meta:
        model = WeatherRecord
        # Inclui todos os campos do modelo WeatherRecord na serialização.
        # Alternativamente, pode listar campos específicos: fields = ['event_id', 'event_name', ...]
        fields = "__all__"
