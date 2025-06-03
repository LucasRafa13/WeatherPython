# api/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from weather_data.models import WeatherRecord  # Importa o modelo WeatherRecord
from .serializers import WeatherRecordSerializer  # Importa o serializador
import re  # Já usado para sanitização
import logging  # Para logging

logger = logging.getLogger(__name__)


# ViewSet para listar e recuperar registos de dados meteorológicos.
class WeatherRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Um ViewSet que fornece automaticamente ações de 'list' e 'retrieve'.
    Utiliza ReadOnlyModelViewSet porque a API é apenas para leitura destes registos.
    """

    queryset = WeatherRecord.objects.all().order_by(
        "event_date", "event_id"
    )  # Consulta base para todos os registos
    serializer_class = WeatherRecordSerializer  # O serializador a ser usado

    # Opcional: Pode adicionar filtros ou lógica personalizada aqui, se necessário.
    # Exemplo: def get_queryset(self): return WeatherRecord.objects.filter(event_location='São Paulo')


# Esta é a view existente para o contexto de um único evento.
@api_view(["GET"])
def event_context_api_view(request, event_id):
    """
    Endpoint REST para obter dados contextuais de um evento específico pelo seu ID.
    """
    try:
        # Tenta encontrar o registo mais recente para o event_id fornecido
        weather_record = (
            WeatherRecord.objects.filter(event_id=event_id)
            .order_by("-loaded_at")
            .first()
        )

        if weather_record:
            # Serializa o objeto WeatherRecord para JSON
            serializer = WeatherRecordSerializer(weather_record)
            logger.info(
                f"Dados do evento ID '{event_id}' encontrados e retornados via API."
            )
            return Response(serializer.data)
        else:
            logger.warning(
                f"Dados do evento ID '{event_id}' não encontrados na base de dados."
            )
            return Response({"error": "Dados do evento não encontrados."}, status=404)
    except Exception as e:
        logger.error(
            f"Erro inesperado na API de contexto de evento para '{event_id}': {e}",
            exc_info=True,
        )
        return Response({"error": "Erro interno do servidor."}, status=500)
