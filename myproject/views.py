# myproject/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from urllib.parse import urlencode  # Para construir URLs com parâmetros
import requests  # Para fazer requisições HTTP internas
import re  # Para sanitizar o event_id


# View para a página inicial com o formulário
def home_view(request):
    return render(request, "weather_query_form.html")


# Nova view para processar a consulta do formulário
def query_weather_data(request):
    if request.method == "GET":
        city = request.GET.get("city")
        date_str = request.GET.get("date")

        if not city or not date_str:
            return JsonResponse(
                {"error": "Cidade e data são obrigatórios."}, status=400
            )

        # Construir o event_id no mesmo formato do comando ingest_weather
        # Ex: EDUARDO_COSTA_SAO_PAULO_20250810
        # Vamos sanitizar a cidade para o event_id
        sanitized_city = re.sub(r"[^a-zA-Z0-9]", "_", city).upper()
        event_id = (
            f"{sanitized_city}_{date_str.replace('-', '')}"  # Ex: SAO_PAULO_20250810
        )

        # Fazer uma requisição interna para a sua própria API de contexto de evento
        # O Django está rodando na porta 8000 dentro do contêiner, mas o curl é externo.
        # Aqui, estamos fazendo uma requisição *interna* do Django para ele mesmo.
        # O host é 'localhost' e a porta '8000' para a requisição interna.
        api_url = f"http://localhost:8000/api/contexto_evento/{event_id}/"

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Levanta um erro para status de erro HTTP
            data = response.json()

            # Redirecionar de volta para a página inicial com os resultados na URL
            # Isso permite que o JavaScript no template exiba os resultados
            return redirect(f"/?result={urlencode({'data': data})}")

        except requests.exceptions.RequestException as e:
            error_message = f"Erro ao consultar a API: {e}"
            print(error_message)
            return redirect(f"/?result={urlencode({'error': error_message})}")
        except Exception as e:
            error_message = f"Erro inesperado: {e}"
            print(error_message)
            return redirect(f"/?result={urlencode({'error': error_message})}")

    return JsonResponse({"error": "Método não permitido."}, status=405)
