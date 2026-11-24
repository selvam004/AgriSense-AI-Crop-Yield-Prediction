from django.contrib import admin
from .models import PredictionRecord, FieldInsightRecord

@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'crop_type', 
        'latitude', 
        'longitude', 
        'predicted_yield', 
        'confidence', 
        'irrigation_used', 
        'created_at'
    )
    list_filter = ('crop_type', 'irrigation_used', 'created_at')
    search_fields = ('crop_type', 'latitude', 'longitude')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(FieldInsightRecord)
class FieldInsightRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'latitude', 
        'longitude', 
        'temperature', 
        'rainfall', 
        'humidity', 
        'soil_ph', 
        'irrigation_status', 
        'recorded_at'
    )
    list_filter = ('irrigation_status', 'recorded_at')
    search_fields = ('latitude', 'longitude')
    readonly_fields = ('recorded_at',)
    ordering = ('-recorded_at',)

# Customize Django Admin Header
admin.site.site_header = "AgriSense Administration"
admin.site.site_title = "AgriSense Portal"
admin.site.index_title = "AgriSense Crop & Soil Analytics Management"
