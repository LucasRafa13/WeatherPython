# events/admin.py
from django.contrib import admin
from .models import Event, IntegrationRun


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "sympla_id", "start_date", "url", "published")
    search_fields = ("name", "sympla_id", "location", "category")
    list_filter = ("published", "category")
    readonly_fields = ("created_at", "updated_at")


@admin.register(IntegrationRun)
class IntegrationRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_time",
        "end_time",
        "status",
        "events_processed",
        "new_events",
        "updated_events",
    )
    list_filter = ("status",)
    readonly_fields = ("start_time", "end_time")
