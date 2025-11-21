from django.contrib import admin
from .models import Crop, WeatherRecord, AbonoApplication

@admin.register(AbonoApplication)
class AbonoApplicationAdmin(admin.ModelAdmin):
    list_display = ("crop", "user", "date_applied", "notes")
    list_filter = ("crop", "user")
    search_fields = ("notes",)

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "country_code", "sowing_date", "created_at")
    search_fields = ("name", "description")

@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("crop", "timestamp", "temperature", "humidity", "rain_mm", "wind_ms")
    list_filter = ("crop",)
