# myproject/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from urllib.parse import urlencode
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
    # ESTA É A LINHA CRUCIAL: Apenas o nome do ficheiro do template.
    # O Django já sabe que 'myproject/templates/' é uma pasta de templates.
    return render(request, "weather_query_form.html")


# View para processar a consulta do formulário.
def query_weather_data(request):
    if request.method == "GET":
        city = request.GET.get("city")
        date_str = request.GET.get("date")

        if not city or not date_str:
            error_message = "Cidade e data são obrigatórios."
            logger.warning(f"Consulta com parâmetros em falta: {city}, {date_str}")
            return redirect(f"/?result={urlencode({'error': error_message})}")

        try:
            event_date = date.fromisoformat(date_str)
        except ValueError:
            error_message = "Formato de data inválido. Use AAAA-MM-DD."
            logger.error(f"Formato de data inválido recebido: {date_str}")
            return redirect(f"/?result={urlencode({'error': error_message})}")

        sanitized_city_for_id = re.sub(r"[^a-zA-Z0-9]", "", city).upper()
        event_id = f"{sanitized_city_for_id}_{date_str.replace('-', '')}"
        event_name = f"Previsão para {city} em {date_str}"

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
                return redirect(
                    f"/?result={urlencode({'data': json.dumps(_serialize_weather_record(existing_record))})}"
                )

            logger.info(
                f"Dados para o evento ID '{event_id}' não encontrados. Iniciando ingestão da WeatherAPI.com."
            )
            weather_data_raw = client.get_weather_forecast(city, event_date)

            if not weather_data_raw:
                error_msg = f"Não foi possível obter dados meteorológicos para '{city}' em '{date_str}' da API externa. Verifique a chave da API ou a conectividade."
                logger.error(error_msg)
                WeatherLoadLog.objects.create(
                    event_id=event_id,
                    log_level="FAILED",
                    message=error_msg,
                    event_name=event_name,
                    event_location=city,
                    event_date=event_date,
                    data_imported_count=0,
                )
                return redirect(f"/?result={urlencode({'error': error_msg})}")

            new_record = WeatherRecord.objects.create(
                event_id=event_id,
                event_name=event_name,
                event_location=city,
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
                message=f"Dados para '{city}' em '{date_str}' ingeridos com sucesso.",
                event_name=event_name,
                event_location=city,
                event_date=event_date,
                data_imported_count=1,
            )
            logger.info(
                f"Dados meteorológicos para o evento ID '{event_id}' ingeridos e logados com sucesso!"
            )

            return redirect(
                f"/?result={urlencode({'data': json.dumps(_serialize_weather_record(new_record))})}"
            )

        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição à WeatherAPI.com: {e}"
            logger.error(error_msg)
            WeatherLoadLog.objects.create(
                event_id=event_id,
                log_level="FAILED",
                message=error_msg,
                event_name=event_name,
                event_location=city,
                event_date=event_date,
                data_imported_count=0,
            )
            return redirect(f"/?result={urlencode({'error': error_msg})}")
        except Exception as e:
            error_msg = f"Erro inesperado durante a ingestão ou processamento: {e}"
            logger.error(error_msg, exc_info=True)
            WeatherLoadLog.objects.create(
                event_id=event_id,
                log_level="FAILED",
                message=error_msg,
                event_name=event_name,
                event_location=city,
                event_date=event_date,
                data_imported_count=0,
            )
            return redirect(f"/?result={urlencode({'error': error_msg})}")

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
