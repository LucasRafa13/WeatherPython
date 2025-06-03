# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from myproject.views import home_view  # Importe a home_view (que agora é o formulário)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),  # A rota /api/ para a API REST (GET e POST)
    path(
        "", home_view, name="home"
    ),  # A rota raiz agora mostra o formulário de ingestão
]
