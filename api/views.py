# api/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from weather_data.models import WeatherRecord, WeatherLoadLog
from weather_data.api_client import WeatherApiClient
from datetime import date
import json
import logging

logger = logging.getLogger(__name__)

# Campos que esperamos receber no POST e os campos correspondentes no modelo
REQUIRED_FIELDS_FOR_INGESTION = [
    "event_name",
    "event_id",
    "city",
    "date",
    "event_location",  # 'city' é para API, 'event_location' para o modelo
]


@method_decorator(
    csrf_exempt, name="dispatch"
)  # Permite POSTs de fora sem token CSRF (para testes)
class WeatherRecordListCreateAPI(View):
    def get(self, request, *args, **kwargs):
        """
        Lista todos os registros de dados meteorológicos.
        Opcional: Filtra por event_id, event_name, event_location ou event_date.
        Ex: /api/?event_id=EVENTO_ID&event_location=Cidade&event_date=YYYY-MM-DD
        """
        records = WeatherRecord.objects.all()

        # Adiciona filtros opcionais via parâmetros de query
        event_id = request.GET.get("event_id")
        event_name = request.GET.get("event_name")
        event_location = request.GET.get("event_location")
        event_date_str = request.GET.get("event_date")

        if event_id:
            records = records.filter(
                event_id__iexact=event_id
            )  # __iexact para case-insensitive
        if event_name:
            records = records.filter(event_name__icontains=event_name)
        if event_location:
            records = records.filter(event_location__icontains=event_location)
        if event_date_str:
            try:
                event_date = date.fromisoformat(event_date_str)
                records = records.filter(event_date=event_date)
            except ValueError:
                return JsonResponse(
                    {"error": "Formato de data inválido. Use YYYY-MM-DD."}, status=400
                )

        # Ordena para ter os mais recentes (maior versão) primeiro para cada evento
        records = records.order_by("event_id", "-loaded_at", "-load_version")

        data = []
        for record in records:
            data.append(
                {
                    "id": record.id,
                    "event_id": record.event_id,
                    "event_name": record.event_name,
                    "event_location": record.event_location,
                    "event_date": record.event_date.isoformat(),  # Formato ISO 8601
                    "temperature": (
                        float(record.temperature)
                        if record.temperature is not None
                        else None
                    ),
                    "feels_like": (
                        float(record.feels_like)
                        if record.feels_like is not None
                        else None
                    ),
                    "min_temperature": (
                        float(record.min_temperature)
                        if record.min_temperature is not None
                        else None
                    ),
                    "max_temperature": (
                        float(record.max_temperature)
                        if record.max_temperature is not None
                        else None
                    ),
                    "humidity": (
                        float(record.humidity) if record.humidity is not None else None
                    ),
                    "pressure": (
                        float(record.pressure) if record.pressure is not None else None
                    ),
                    "wind_speed": (
                        float(record.wind_speed)
                        if record.wind_speed is not None
                        else None
                    ),
                    "weather_main": record.weather_main,
                    "weather_description": record.weather_description,
                    "api_source": record.api_source,
                    "load_version": record.load_version,
                    "loaded_at": record.loaded_at.isoformat(),
                }
            )
        return JsonResponse(data, safe=False, status=200)

    def post(self, request, *args, **kwargs):
        """
        Cria um novo registro de dados meteorológicos usando dados fornecidos.
        Espera um JSON no corpo da requisição com:
        {
            "event_name": "Nome do Evento",
            "event_id": "ID_DO_EVENTO_UNICO",
            "city": "Nome da Cidade, País",
            "date": "YYYY-MM-DD"
        }
        """
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Requisição JSON inválida."}, status=400)

        # Validação básica dos campos
        missing_fields = [f for f in REQUIRED_FIELDS_FOR_INGESTION if f not in payload]
        if missing_fields:
            return JsonResponse(
                {"error": f"Campos obrigatórios faltando: {', '.join(missing_fields)}"},
                status=400,
            )

        event_name = payload.get("event_name")
        event_id = payload.get("event_id")
        city = payload.get("city")
        event_date_str = payload.get("date")
        event_location = payload.get(
            "city"
        )  # Reutiliza 'city' como event_location para o modelo

        try:
            event_date = date.fromisoformat(event_date_str)
        except ValueError:
            return JsonResponse(
                {"error": "Formato de data inválido. Use YYYY-MM-DD."}, status=400
            )

        client = WeatherApiClient()
        try:
            weather_data_raw = client.get_weather_forecast(city, event_date)

            if not weather_data_raw:
                error_msg = f"Não foi possível obter dados meteorológicos para {city} em {event_date_str}. Verifique a data (limite de 3 dias do plano free) ou a localização."
                logger.error(error_msg)
                WeatherLoadLog.objects.create(
                    event_id=event_id,
                    log_level="ERROR",
                    message=error_msg,
                    event_name=event_name,
                    event_location=event_location,
                    event_date=event_date,
                    data_imported_count=0,
                )
                return JsonResponse({"error": error_msg}, status=500)

            # Lógica de versionamento: Encontra a última versão e incrementa
            latest_record = (
                WeatherRecord.objects.filter(
                    event_id=event_id,
                    event_location=event_location,
                    event_date=event_date,
                )
                .order_by("-load_version")
                .first()
            )

            new_version = 1
            if latest_record:
                new_version = latest_record.load_version + 1

            new_record = WeatherRecord.objects.create(
                event_id=event_id,
                event_name=event_name,
                event_location=event_location,
                event_date=event_date,
                temperature=weather_data_raw.get("temperature"),
                feels_like=weather_data_raw.get("feels_like"),
                min_temperature=weather_data_raw.get("min_temperature"),
                max_temperature=weather_data_raw.get("max_temperature"),
                humidity=weather_data_raw.get("humidity"),
                pressure=weather_data_raw.get("pressure"),
                wind_speed=weather_data_raw.get("wind_speed"),
                weather_main=weather_data_raw.get("weather_main"),
                weather_description=weather_data_raw.get("weather_description"),
                api_source="WeatherAPI.com",
                load_version=new_version,
            )

            WeatherLoadLog.objects.create(
                event_id=event_id,
                log_level="SUCCESS",
                message=f"Dados para {city} em {event_date_str} ingeridos via API com sucesso. Versão: {new_version}",
                event_name=event_name,
                event_location=event_location,
                event_date=event_date,
                data_imported_count=1,
            )

            return JsonResponse(
                {
                    "message": "Dados ingeridos e logados com sucesso via API!",
                    "record_id": new_record.id,
                    "load_version": new_record.load_version,
                },
                status=201,
            )  # 201 Created

        except Exception as e:
            error_message = f"Erro inesperado ao criar registro via API: {e}"
            logger.error(
                error_message, exc_info=True
            )  # exc_info para logar o traceback completo
            WeatherLoadLog.objects.create(
                event_id=event_id,
                log_level="ERROR",
                message=error_message,
                event_name=event_name,
                event_location=event_location,
                event_date=event_date,
                data_imported_count=0,
            )
            return JsonResponse(
                {"error": "Erro interno do servidor.", "details": str(e)}, status=500
            )
