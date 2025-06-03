from flask import Flask, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv
from datetime import date

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# --- Configuração do Banco de Dados ---
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}


def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


@app.route("/")
def home():
    """Rota inicial para verificar se a API está funcionando."""
    return "API de Contexto de Eventos está online!"


@app.route("/contexto_evento/<string:event_id>", methods=["GET"])
def get_event_context(event_id):
    """
    Retorna os dados contextuais para um determinado ID de evento.
    Exemplo: /contexto_evento/EDUARDO_COSTA_CUIABA_20250820
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Falha na conexão com o banco de dados."}), 500

        cur = conn.cursor()

        # Busca o dado contextual mais recente para o event_id
        # Ordena por data_retrieval_timestamp para pegar a informação mais fresca, se houver múltiplas
        cur.execute(
            """
            SELECT context_data
            FROM event_context_data
            WHERE event_id = %s
            ORDER BY data_retrieval_timestamp DESC
            LIMIT 1;
            """,
            (event_id,),
        )

        result = cur.fetchone()

        if result:
            # context_data é armazenado como JSONB, então psycopg2 o retorna como um dicionário Python
            return jsonify(result[0]), 200
        else:
            return (
                jsonify(
                    {
                        "message": f"Nenhum dado contextual encontrado para o evento ID: {event_id}"
                    }
                ),
                404,
            )

    except psycopg2.Error as e:
        print(f"Erro no banco de dados ao buscar contexto do evento: {e}")
        return jsonify({"error": "Erro interno do servidor ao buscar dados."}), 500
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return jsonify({"error": "Erro interno inesperado."}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# Esta parte só é executada se você rodar o script Python diretamente,
# e não via 'flask run' ou Gunicorn. No Docker Compose, 'flask run' é usado.
if __name__ == "__main__":
    # Usar porta e host do ambiente se disponíveis, caso contrário, padrões
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    app.run(debug=True, host=host, port=port)
