# weather_data/management/commands/ingest_weather.py

from django.core.management.base import BaseCommand, CommandError
from weather_data.models import WeatherRecord, WeatherLoadLog
from weather_data.api_client import WeatherApiClient
from datetime import date  # Importe datetime para usar timedelta
import logging
import json  # Não está sendo usado, pode ser removido se não for necessário

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Ingere dados meteorológicos para um evento específico da WeatherAPI.com."

    def add_arguments(self, parser):
        parser.add_argument(
            "--city",
            type=str,
            help="Nome da cidade para a qual ingerir dados meteorológicos.",
            required=True,
        )
        parser.add_argument(
            "--date",
            type=str,  # Mantém como string na entrada do comando
            help="Data do evento no formato YYYY-MM-DD (ex: 2025-08-10).",
            required=True,
        )
        parser.add_argument(
            "--event_id",
            type=str,
            help="ID único do evento (ex: EDUARDO_COSTA_SAO_PAULO_20250810).",
            required=True,
        )
        parser.add_argument(
            "--event_name",
            type=str,
            help="Nome do evento (ex: Eduardo Costa).",
            required=True,
        )

    def handle(self, *args, **options):
        city = options["city"]
        event_date_str = options["date"]
        event_id = options["event_id"]
        event_name = options["event_name"]

        try:
            # Converte a string da data para um objeto datetime.date AQUI
            event_date = date.fromisoformat(event_date_str)
        except ValueError:
            raise CommandError(
                f"Formato de data inválido. Use YYYY-MM-DD. Recebido: {event_date_str}"
            )

        self.stdout.write(
            self.style.NOTICE(
                f"Iniciando ingestão de dados para o evento {event_id} em {city} na data {event_date_str}..."
            )
        )

        client = WeatherApiClient()
        try:
            # PASSA O OBJETO datetime.date (event_date), NÃO A STRING (event_date_str)
            weather_data_raw = client.get_weather_forecast(
                city, event_date
            )  # <-- CORREÇÃO AQUI!

            if not weather_data_raw:
                # Modificado para logar um erro mais específico se a API retornar None
                error_msg = f"Não foi possível obter dados meteorológicos para {city} em {event_date_str}. Verifique a data (limite de 3 dias do plano free) ou a localização."
                self.stderr.write(self.style.ERROR(error_msg))
                WeatherLoadLog.objects.create(
                    event_id=event_id,
                    log_level="ERROR",  # Mudado para ERROR para falha na obtenção
                    message=error_msg,
                    event_name=event_name,
                    event_location=city,
                    event_date=event_date,
                    data_imported_count=0,
                )
                raise CommandError(
                    error_msg
                )  # Levanta CommandError para parar o comando

            # Lógica de versionamento: Encontra a última versão e incrementa
            # (Este bloco pode ser adicionado aqui para versionamento)
            latest_record = (
                WeatherRecord.objects.filter(
                    event_id=event_id, event_location=city, event_date=event_date
                )
                .order_by("-load_version")
                .first()
            )

            new_version = 1
            if latest_record:
                new_version = latest_record.load_version + 1

            WeatherRecord.objects.create(
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
                load_version=new_version,  # Usando a nova versão
            )

            WeatherLoadLog.objects.create(
                event_id=event_id,
                log_level="SUCCESS",
                message=f"Dados para {city} em {event_date_str} ingeridos com sucesso. Versão: {new_version}",
                event_name=event_name,
                event_location=city,
                event_date=event_date,
                data_imported_count=1,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Dados meteorológicos para {event_id} ingeridos e logados com sucesso! Versão: {new_version}"
                )
            )

        except CommandError as e:
            # CommandError já é tratado e logado no início do bloco try
            pass  # Não precisa fazer nada aqui, o log já foi feito antes de levantar o erro
        except Exception as e:
            # Este é para erros inesperados não capturados por CommandError
            error_message = f"Erro inesperado durante a ingestão: {e}"
            self.stderr.write(self.style.ERROR(error_message))
            WeatherLoadLog.objects.create(
                event_id=event_id,
                log_level="ERROR",  # Mudado para ERROR
                message=error_message,
                event_name=event_name,
                event_location=city,
                event_date=event_date,
                data_imported_count=0,
            )
            raise  # Re-lança a exceção para que o comando falhe
