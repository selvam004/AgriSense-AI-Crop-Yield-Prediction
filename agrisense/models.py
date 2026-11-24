from django.db import models

class PredictionRecord(models.Model):
    CROP_CHOICES = [
        ('Wheat', 'Wheat'),
        ('Rice', 'Rice'),
        ('Maize', 'Maize'),
        ('Soybean', 'Soybean'),
    ]

    latitude = models.FloatField(help_text="Farm latitude coordinate")
    longitude = models.FloatField(help_text="Farm longitude coordinate")
    crop_type = models.CharField(max_length=50, choices=CROP_CHOICES)
    planting_date = models.DateField()
    irrigation_used = models.BooleanField(default=False)
    
    # Results
    predicted_yield = models.FloatField(help_text="Yield in tons/ha")
    confidence = models.IntegerField(help_text="Confidence percentage (0-100)")
    soil_suitability = models.CharField(max_length=255, blank=True)
    growth_potential = models.CharField(max_length=255, blank=True)
    tips = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prediction Record'
        verbose_name_plural = 'Prediction Records'

    def __str__(self):
        return f"{self.crop_type} ({self.latitude:.2f}, {self.longitude:.2f}) -> {self.predicted_yield} t/ha"


class FieldInsightRecord(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Weather
    temperature = models.FloatField(help_text="Temperature in °C")
    rainfall = models.FloatField(help_text="Rainfall in mm")
    humidity = models.FloatField(help_text="Humidity in %")
    
    # Soil Health
    soil_ph = models.FloatField(help_text="Soil pH (0-14)")
    organic_carbon = models.FloatField(help_text="Organic Carbon %")
    nitrogen = models.FloatField(help_text="Nitrogen in mg/kg")
    
    # Irrigation
    irrigation_status = models.CharField(max_length=50)
    irrigation_efficiency = models.IntegerField(help_text="Efficiency percentage")
    water_index = models.FloatField(help_text="Water index score")
    
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Field Insight Record'
        verbose_name_plural = 'Field Insight Records'

    def __str__(self):
        return f"Insight @ ({self.latitude:.2f}, {self.longitude:.2f}) - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
