# myproject/views.py
from django.shortcuts import render
from django.http import JsonResponse
import requests
import re
from datetime import date
import os
import logging
import json

from weather_data.models import WeatherRecord, WeatherLoadLog
from weather_data.api_client import WeatherApiClient

logger = logging.getLogger(__name__)


# View para a página inicial que exibe o formulário de consulta de clima.
def home_view(request):
    return render(request, "weather_query_form.html")


# View para processar a consulta inicial do formulário.
# Esta view agora retorna JSON diretamente para o frontend.
def query_weather_data(request):
    if request.method == "GET":
        event_name = request.GET.get("event_name")
        city = request.GET.get("city")
        date_str = request.GET.get("date")

        if not event_name or not city or not date_str:
            return JsonResponse(
                {
                    "error": "Todos os campos (Nome do Evento, Cidade e Data) são obrigatórios."
                },
                status=400,
            )

        try:
            event_date = date.fromisoformat(date_str)
        except ValueError:
            return JsonResponse(
                {"error": "Formato de data inválido. Use AAAA-MM-DD."}, status=400
            )

        sanitized_event_name_for_id = re.sub(r"[^a-zA-Z0-9]", "", event_name).upper()
        sanitized_city_for_id = re.sub(r"[^a-zA-Z0-9]", "", city).upper()
        event_id = f"{sanitized_event_name_for_id}_{sanitized_city_for_id}_{date_str.replace('-', '')}"

        client = WeatherApiClient()

        try:
            existing_record = (
                WeatherRecord.objects.filter(event_id=event_id)
                .order_by("-loaded_at")
                .first()
            )

            if existing_record:
                logger.info(
                    f"Dados para o evento ID '{event_id}' já existem no DB. Exibindo registo existente."
                )
                return JsonResponse(
                    {
                        "data": _serialize_weather_record(existing_record),
                        "status": "existing",
                    },
                    status=200,
                )

            logger.info(
                f"Dados para o evento ID '{event_id}' não encontrados. Iniciando ingestão da WeatherAPI.com."
            )
            weather_data_raw = client.get_weather_forecast(city, event_date)

            if not weather_data_raw:
                error_msg = f"Não foi possível obter dados meteorológicos para '{city}' em '{date_str}' da API externa. Verifique a chave da API ou a conectividade."
                logger.error(error_msg)
                return JsonResponse({"error": error_msg}, status=500)

            response_data = {
                "event_id": event_id,
                "event_name": event_name,
                "event_location": city,
                "event_date": date_str,
                "weather_data": weather_data_raw,
                "status": "new_fetched",
            }
            return JsonResponse({"data": response_data}, status=200)

        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição à WeatherAPI.com: {e}"
            logger.error(error_msg)
            return JsonResponse({"error": error_msg}, status=500)
        except Exception as e:
            error_msg = f"Erro inesperado durante a consulta: {e}"
            logger.error(error_msg, exc_info=True)
            return JsonResponse({"error": error_msg}, status=500)

    return JsonResponse({"error": "Método não permitido."}, status=405)


# NOVA View para salvar os dados no banco de dados (chamada via AJAX POST)
def save_weather_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            event_id = data.get("event_id")
            event_name = data.get("event_name")
            event_location = data.get("event_location")
            event_date_str = data.get("event_date")
            weather_data_raw = data.get("weather_data")

            if not all(
                [event_id, event_name, event_location, event_date_str, weather_data_raw]
            ):
                return JsonResponse(
                    {"error": "Dados incompletos para salvar."}, status=400
                )

            event_date = date.fromisoformat(event_date_str)

            if WeatherRecord.objects.filter(event_id=event_id).exists():
                return JsonResponse(
                    {
                        "message": f"Dados para o evento ID '{event_id}' já estão salvos."
                    },
                    status=200,
                )

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
                load_version=1,
            )

            WeatherLoadLog.objects.create(
                event_id=event_id,
                log_level="SUCCESS",
                message=f"Dados para '{event_location}' em '{event_date_str}' salvos com sucesso.",
                event_name=event_name,
                event_location=event_location,
                event_date=event_date,
                data_imported_count=1,
            )
            logger.info(f"Dados do evento ID '{event_id}' salvos no DB com sucesso.")

            return JsonResponse(
                {
                    "message": "Dados salvos com sucesso! Acesse /api para vizualização",
                    "event_id": event_id,
                },
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido."}, status=400)
        except Exception as e:
            error_msg = f"Erro inesperado ao salvar dados: {e}"
            logger.error(error_msg, exc_info=True)
            return JsonResponse({"error": error_msg}, status=500)

    return JsonResponse({"error": "Método não permitido."}, status=405)


def _serialize_weather_record(record):
    return {
        "event_id": record.event_id,
        "event_name": record.event_name,
        "event_location": record.event_location,
        "event_date": record.event_date.isoformat(),
        "temperature": (
            float(record.temperature) if record.temperature is not None else None
        ),
        "feels_like": (
            float(record.feels_like) if record.feels_like is not None else None
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
        "humidity": float(record.humidity) if record.humidity is not None else None,
        "pressure": float(record.pressure) if record.pressure is not None else None,
        "wind_speed": (
            float(record.wind_speed) if record.wind_speed is not None else None
        ),
        "weather_main": record.weather_main,
        "weather_description": record.weather_description,
        "api_source": record.api_source,
        "loaded_at": record.loaded_at.isoformat(),
    }
