# weather_data/models.py
from django.db import models


class WeatherRecord(models.Model):
    event_id = models.CharField(max_length=255)  # REMOVA unique=True daqui!
    event_name = models.CharField(max_length=255)
    event_location = models.CharField(max_length=255)
    event_date = models.DateField()
    temperature = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    feels_like = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    min_temperature = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    max_temperature = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    humidity = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    pressure = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    wind_speed = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    weather_main = models.CharField(max_length=100, null=True, blank=True)
    weather_description = models.CharField(max_length=255, null=True, blank=True)
    api_source = models.CharField(max_length=100)
    load_version = models.IntegerField(
        default=1
    )  # Este campo é crucial para o versionamento
    loaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garante que CADA COMBINAÇÃO de evento, localização, data E VERSÃO é única.
        # Isso permite múltiplas versões do MESMO evento.
        unique_together = ("event_id", "event_location", "event_date", "load_version")
        ordering = [
            "event_id",
            "event_date",
            "load_version",
        ]  # Opcional: para ordenar resultados

    def __str__(self):
        return f"{self.event_name} ({self.event_location}) - {self.event_date} (V{self.load_version})"


# Certifique-se de que WeatherLoadLog também está como esperado
class WeatherLoadLog(models.Model):
    event_id = models.CharField(max_length=255)
    log_level = models.CharField(max_length=50)  # SUCCESS, FAILED, ERROR
    message = models.TextField()
    event_name = models.CharField(max_length=255, null=True, blank=True)
    event_location = models.CharField(max_length=255, null=True, blank=True)
    event_date = models.DateField(null=True, blank=True)
    data_imported_count = models.IntegerField(default=0)
    loaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.loaded_at.strftime('%Y-%m-%d %H:%M:%S')}] {self.log_level}: {self.message}"


class WeatherLoadLog(models.Model):
    event_id = models.CharField(max_length=255)
    log_level = models.CharField(max_length=50)
    message = models.TextField()
    event_name = models.CharField(max_length=255, null=True, blank=True)
    event_location = models.CharField(max_length=255, null=True, blank=True)
    event_date = models.DateField(null=True, blank=True)
    data_imported_count = models.IntegerField(default=0)
    loaded_at = models.DateTimeField(
        auto_now_add=True
    )  # <-- Esta linha deve estar aqui!

    def __str__(self):
        return f"[{self.loaded_at.strftime('%Y-%m-%d %H:%M:%S')}] {self.log_level}: {self.message}"
