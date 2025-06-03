# events/models.py

from django.db import models
from django.utils import timezone  # Importe timezone para timestamps


class Event(models.Model):
    """
    Modelo para representar um evento da Sympla.
    """

    sympla_id = models.CharField(
        max_length=255, unique=True, help_text="ID único do evento na Sympla"
    )
    name = models.CharField(max_length=500, help_text="Nome do evento")
    start_date = models.DateTimeField(help_text="Data e hora de início do evento")
    end_date = models.DateTimeField(
        help_text="Data e hora de término do evento", null=True, blank=True
    )
    image_url = models.URLField(
        max_length=1000, null=True, blank=True, help_text="URL da imagem do evento"
    )
    category = models.CharField(
        max_length=255, null=True, blank=True, help_text="Categoria do evento"
    )
    producer = models.CharField(
        max_length=255, null=True, blank=True, help_text="Produtor do evento"
    )
    location = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Local do evento (Cidade, Estado, etc.)",
    )
    url = models.URLField(max_length=1000, help_text="URL do evento na Sympla")
    published = models.BooleanField(
        default=True, help_text="Indica se o evento está publicado"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp de criação no banco de dados"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp da última atualização no banco de dados"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["start_date"]  # Ordenar eventos por data de início padrão
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"


class IntegrationRun(models.Model):
    """
    Modelo para registrar cada execução da integração com a API da Sympla.
    """

    start_time = models.DateTimeField(
        auto_now_add=True, help_text="Início da execução da integração"
    )
    end_time = models.DateTimeField(
        null=True, blank=True, help_text="Fim da execução da integração"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("SUCCESS", "Sucesso"),
            ("FAILED", "Falha"),
            ("RUNNING", "Em Execução"),
        ],
        default="RUNNING",
        help_text="Status da execução da integração",
    )
    events_processed = models.IntegerField(
        default=0, help_text="Número de eventos processados"
    )
    new_events = models.IntegerField(
        default=0, help_text="Número de novos eventos criados"
    )
    updated_events = models.IntegerField(
        default=0, help_text="Número de eventos atualizados"
    )
    error_message = models.TextField(
        null=True, blank=True, help_text="Mensagem de erro, se houver"
    )

    def __str__(self):
        return f"Execução {self.id} - {self.status} ({self.start_time.strftime('%Y-%m-%d %H:%M:%S')})"

    class Meta:
        ordering = ["-start_time"]  # Ordenar execuções pela mais recente
        verbose_name = "Execução de Integração"
        verbose_name_plural = "Execuções de Integração"
