import requests
from datetime import datetime, timezone, date, timedelta
import json
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração ---
# Coordenadas de Cuiabá, MT, Brasil (aproximadas)
LATITUDE_CUIABA = -15.5959
LONGITUDE_CUIABA = -56.0984

DATA_EVENTO_STR = "20/08/2025"  # Data simulada do evento no formato DD/MM/YYYY
ID_EVENTO_SIMULADO = "EDUARDO_COSTA_CUIABA_20250820"  # ID único para o evento simulado

# --- Configuração do Banco de Dados (PostgreSQL) ---
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

# --- Importar a função persist_data (permanece a mesma, mas está aqui para referência) ---
import psycopg2


def fetch_openmeteo_weather_data(lat, lon, start_date, end_date):
    """
    Busca dados de previsão diária da Open-Meteo Weather API.
    A API é gratuita e não requer chave.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,wind_speed_10m_max,uv_index_max",
        "timezone": "America/Sao_Paulo",  # Cuiabá está no fuso horário de São Paulo (-3)
        "start_date": start_date.isoformat(),  # Formato YYYY-MM-DD
        "end_date": end_date.isoformat(),  # Formato YYYY-MM-DD
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados climáticos da Open-Meteo API: {e}")
        return None


def get_weather_code_description(code):
    """
    Mapeia os códigos de clima da Open-Meteo para descrições legíveis.
    Fonte: https://www.open-meteo.com/en/docs
    """
    # Exemplo simplificado. Uma implementação completa usaria um dicionário maior.
    # Você pode expandir isso para todos os códigos da documentação.
    descriptions = {
        0: "Céu limpo",
        1: "Principalmente limpo",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Nevoeiro",
        48: "Nevoeiro com deposição de orvalho",
        51: "Chuvisco leve",
        53: "Chuvisco moderado",
        55: "Chuvisco denso",
        56: "Chuvisco congelante leve",
        57: "Chuvisco congelante denso",
        61: "Chuva leve",
        63: "Chuva moderada",
        65: "Chuva forte",
        66: "Chuva congelante leve",
        67: "Chuva congelante forte",
        71: "Queda de neve leve",
        73: "Queda de neve moderada",
        75: "Queda de neve forte",
        77: "Grãos de neve",
        80: "Pancadas de chuva leves",
        81: "Pancadas de chuva moderadas",
        82: "Pancadas de chuva violentas",
        85: "Pancadas de neve leves",
        86: "Pancadas de neve fortes",
        95: "Tempestade com chuva leve e moderada",
        96: "Tempestade com granizo leve",
        99: "Tempestade com granizo forte",
    }
    return descriptions.get(code, "Desconhecido")


def normalize_openmeteo_daily_data(raw_data, target_date_str):
    """
    Normaliza os dados diários da Open-Meteo API para um formato consistente,
    focando na data alvo do evento.
    """
    if not raw_data or "daily" not in raw_data or "time" not in raw_data["daily"]:
        print(
            "Dados brutos inválidos ou estrutura 'daily' ausente na resposta da Open-Meteo."
        )
        return None

    target_date_dt = datetime.strptime(target_date_str, "%d/%m/%Y").date()

    # A API retorna listas de dados, onde cada índice corresponde a um dia na lista 'time'
    daily_times = [datetime.fromisoformat(t).date() for t in raw_data["daily"]["time"]]

    try:
        # Encontra o índice da data do evento na lista de tempos
        day_index = daily_times.index(target_date_dt)
    except ValueError:
        print(
            f"Previsão para a data {target_date_str} não encontrada na resposta da API."
        )
        return None

    # Extrai os dados para o dia específico usando o índice
    daily_data_for_target_date = {
        "time": raw_data["daily"]["time"][day_index],
        "temperature_2m_max": raw_data["daily"]["temperature_2m_max"][day_index],
        "temperature_2m_min": raw_data["daily"]["temperature_2m_min"][day_index],
        "weather_code": raw_data["daily"]["weather_code"][day_index],
        "precipitation_sum": raw_data["daily"]["precipitation_sum"][day_index],
        "wind_speed_10m_max": raw_data["daily"]["wind_speed_10m_max"][day_index],
        "uv_index_max": raw_data["daily"]["uv_index_max"][day_index],
    }

    try:
        normalized = {
            "event_id": ID_EVENTO_SIMULADO,
            "context_type": "WEATHER_FORECAST_DAILY",
            "nome_cidade_fuso_horario": raw_data.get("timezone", "N/A"),
            "latitude": raw_data.get("latitude"),
            "longitude": raw_data.get("longitude"),
            "data_previsao": daily_data_for_target_date[
                "time"
            ],  # Já está em YYYY-MM-DD
            "temperatura_max_celsius": daily_data_for_target_date["temperature_2m_max"],
            "temperatura_min_celsius": daily_data_for_target_date["temperature_2m_min"],
            "codigo_clima": daily_data_for_target_date["weather_code"],
            "descricao_clima": get_weather_code_description(
                daily_data_for_target_date["weather_code"]
            ),
            "soma_precipitacao_mm": daily_data_for_target_date["precipitation_sum"],
            "velocidade_vento_max_ms": daily_data_for_target_date["wind_speed_10m_max"],
            "uv_index_max": daily_data_for_target_date["uv_index_max"],
            "timestamp_coleta_dados": datetime.now(
                timezone.utc
            ).isoformat(),  # Quando coletamos este dado
            "data_evento_simulado": target_date_dt.isoformat(),  # Data do evento para a qual a previsão é
        }
        return normalized
    except Exception as e:
        print(f"Erro ao normalizar dados diários específicos da Open-Meteo: {e}")
        return None


# --- Funções de Persistência (Mantidas as mesmas do script anterior) ---


def persist_data(
    normalized_data, simulated_event_id, source_name="Open-Meteo Weather API"
):
    """Persiste os dados normalizados no banco de dados e registra a carga."""
    conn = None
    cur = None
    load_id = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO data_load_log (source_name, status, records_imported)
            VALUES (%s, %s, %s)
            RETURNING load_id;
            """,
            (source_name, "IN_PROGRESS", 0),
        )
        load_id = cur.fetchone()[0]
        conn.commit()

        if normalized_data:
            event_date_obj = date.fromisoformat(normalized_data["data_evento_simulado"])
            retrieval_timestamp_obj = datetime.fromisoformat(
                normalized_data["timestamp_coleta_dados"]
            )

            cur.execute(
                """
                INSERT INTO event_context_data (
                    event_id, context_type, context_data,
                    event_simulated_date, data_retrieval_timestamp, load_id
                ) VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (
                    simulated_event_id,
                    normalized_data["context_type"],
                    json.dumps(normalized_data),
                    event_date_obj,
                    retrieval_timestamp_obj,
                    load_id,
                ),
            )
            cur.execute(
                """
                UPDATE data_load_log
                SET status = %s, records_imported = %s
                WHERE load_id = %s;
                """,
                ("SUCCESS", 1, load_id),
            )
            conn.commit()
            print(f"Dados persistidos com sucesso com load_id: {load_id}")
            return True
        else:
            cur.execute(
                """
                UPDATE data_load_log
                SET status = %s, error_message = %s, records_imported = %s
                WHERE load_id = %s;
                """,
                ("ERROR", "Nenhum dado normalizado para persistir", 0, load_id),
            )
            conn.commit()
            print(
                f"Nenhum dado para persistir. Erro registrado para load_id: {load_id}"
            )
            return False

    except (Exception, psycopg2.Error) as error:
        print(f"Erro durante a persistência dos dados: {error}")
        if conn:
            conn.rollback()
            if load_id:
                try:
                    cur_error = conn.cursor()
                    cur_error.execute(
                        """
                        UPDATE data_load_log
                        SET status = %s, error_message = %s
                        WHERE load_id = %s;
                        """,
                        ("ERROR", str(error), load_id),
                    )
                    conn.commit()
                except Exception as update_error:
                    print(
                        f"Erro ao tentar atualizar o log de carga após falha: {update_error}"
                    )
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print(
        f"Iniciando processo de ingestão de previsão diária para o evento: {ID_EVENTO_SIMULADO}"
    )
    print(f"Data do evento: {DATA_EVENTO_STR}")

    # Converte a DATA_EVENTO_STR para um objeto date
    target_date_obj = datetime.strptime(DATA_EVENTO_STR, "%d/%m/%Y").date()

    # Open-Meteo usa start_date e end_date. Para uma previsão de um único dia, defina-os como a mesma data.
    raw_data = fetch_openmeteo_weather_data(
        LATITUDE_CUIABA, LONGITUDE_CUIABA, target_date_obj, target_date_obj
    )

    if raw_data:
        # A função de normalização precisa encontrar os dados para a data específica
        normalized_data = normalize_openmeteo_daily_data(raw_data, DATA_EVENTO_STR)
    else:
        normalized_data = None

    if normalized_data:
        print("\nDados Normalizados (para persistência):")
        for k, v in normalized_data.items():
            print(f"  {k}: {v}")

        success = persist_data(normalized_data, ID_EVENTO_SIMULADO)
        if success:
            print("\nProcesso de ingestão de dados concluído com sucesso.")
        else:
            print("\nProcesso de ingestão de dados falhou.")
    else:
        print(
            "Não foi possível buscar ou normalizar a previsão diária para a data do evento. Abortando persistência."
        )
