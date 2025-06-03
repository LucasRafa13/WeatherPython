
import requests
from decouple import config
import datetime
from datetime import timedelta  # Importe timedelta aqui


class WeatherApiClient:
    def __init__(self):
        self.api_key = config("WEATHER_API_KEY")
        self.base_url = "http://api.weatherapi.com/v1/forecast.json"

    # forecast_date AGORA ESPERA UM OBJETO datetime.date
    def get_weather_forecast(self, event_location, forecast_date: datetime.date):
        """
        Busca a previsão do tempo para uma localização e data específica usando WeatherAPI.com.
        A WeatherAPI.com (plano gratuito) oferece previsão de 3 dias.
        Queries podem ser por cidade, CEP, lat/lon. Usaremos a localização textual.
        """
        query_location = event_location

        today = datetime.date.today()
        # AGORA forecast_date É UM OBJETO datetime.date, então a subtração funciona
        num_days = (forecast_date - today).days + 1

        if num_days > 3 or num_days < 1:
            print(
                f"Atenção: A WeatherAPI.com (plano gratuito) só fornece previsão para os próximos 3 dias."
            )
            print(
                f"A data do evento {forecast_date} está fora do período de cobertura."
            )
            return None

        params = {
            "key": self.api_key,
            "q": query_location,
            "days": num_days,
            "aqi": "no",
            "alerts": "no",
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if (
                not data
                or "forecast" not in data
                or "forecastday" not in data["forecast"]
            ):
                print(f"Resposta inesperada da WeatherAPI.com: {data}")
                return None

            daily_forecast_for_event = None
            for daily_entry in data["forecast"]["forecastday"]:
                entry_date_str = daily_entry["date"]
                entry_date = datetime.datetime.strptime(
                    entry_date_str, "%Y-%m-%d"
                ).date()

                if entry_date == forecast_date:
                    daily_forecast_for_event = daily_entry["day"]
                    break

            if daily_forecast_for_event:
                wind_speed_kph = daily_forecast_for_event.get("maxwind_kph")
                wind_speed_mps = (
                    round(wind_speed_kph / 3.6, 2)
                    if wind_speed_kph is not None
                    else None
                )

                return {
                    "temperature": daily_forecast_for_event.get("avgtemp_c"),
                    "min_temperature": daily_forecast_for_event.get("mintemp_c"),
                    "max_temperature": daily_forecast_for_event.get("maxtemp_c"),
                    "feels_like": daily_forecast_for_event.get("avgtemp_c"),
                    "humidity": daily_forecast_for_event.get("avghumidity"),
                    "pressure": None,
                    "wind_speed": wind_speed_mps,
                    "weather_main": daily_forecast_for_event["condition"].get("text"),
                    "weather_description": daily_forecast_for_event["condition"].get(
                        "text"
                    ),
                }

            print(
                f"Previsão para {forecast_date} não encontrada na resposta da WeatherAPI.com."
            )
            return None

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição à WeatherAPI.com: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao processar dados da WeatherAPI.com: {e}")
            return None


# Exemplo de uso (para testar diretamente este arquivo)
if __name__ == "__main__":
    # Para testar este arquivo diretamente, você precisaria definir a variável de ambiente:
    # import os
    # os.environ['WEATHER_API_KEY'] = 'SUA_CHAVE_AQUI'

    client = WeatherApiClient()

    event_location_sp = "Cuiaba, Brazil"

    event_date_today = datetime.date.today()
    event_date_tomorrow = datetime.date.today() + timedelta(days=1)
    event_date_day_after = datetime.date.today() + timedelta(days=2)

    print("\n--- Testando para hoje ---")
    weather_data_today = client.get_weather_forecast(
        event_location_sp, event_date_today
    )
    if weather_data_today:
        print(
            f"Dados meteorológicos para {event_location_sp} em {event_date_today} (WeatherAPI.com):"
        )
        for key, value in weather_data_today.items():
            print(f"  {key}: {value}")
    else:
        print(
            f"Não foi possível obter dados meteorológicos para {event_location_sp} em {event_date_today}."
        )

    print("\n--- Testando para amanhã ---")
    weather_data_tomorrow = client.get_weather_forecast(
        event_location_sp, event_date_tomorrow
    )
    if weather_data_tomorrow:
        print(
            f"Dados meteorológicos para {event_location_sp} em {event_date_tomorrow} (WeatherAPI.com):"
        )
        for key, value in weather_data_tomorrow.items():
            print(f"  {key}: {value}")
    else:
        print(
            f"Não foi possível obter dados meteorológicos para {event_location_sp} em {event_date_tomorrow}."
        )
