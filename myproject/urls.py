# myproject/urls.py
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Adicione suas outras rotas aqui depois
]
