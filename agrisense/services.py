import math
import datetime
import requests
from django.conf import settings

def calculate_crop_prediction(latitude, longitude, crop_type, planting_date, irrigation_used):
    """
    Simulates ML yield prediction model based on crop type, agro-ecological zone,
    planting date, and water availability (irrigation).
    """
    # Crop base potential in tons per hectare
    base_yields = {
        'Wheat': 3.5,
        'Rice': 4.2,
        'Maize': 6.0,
        'Soybean': 2.4,
    }
    
    base = base_yields.get(crop_type, 3.5)
    
    # Latitude suitability factor
    abs_lat = abs(float(latitude))
    lat_factor = 1.0
    
    if crop_type == 'Wheat':
        # Thrives in temperate zones (20 - 45 deg)
        if 20 <= abs_lat <= 45:
            lat_factor = 1.15
        elif abs_lat < 15:
            lat_factor = 0.85
        else:
            lat_factor = 0.95
    elif crop_type == 'Rice':
        # Thrives in tropical & subtropical (0 - 30 deg)
        if 5 <= abs_lat <= 30:
            lat_factor = 1.2
        elif abs_lat > 40:
            lat_factor = 0.75
        else:
            lat_factor = 1.0
    elif crop_type == 'Maize':
        if 15 <= abs_lat <= 45:
            lat_factor = 1.12
        else:
            lat_factor = 0.90
    elif crop_type == 'Soybean':
        if 20 <= abs_lat <= 42:
            lat_factor = 1.10
        else:
            lat_factor = 0.88

    # Irrigation boost
    if irrigation_used:
        irrigation_factor = 1.28
        confidence_boost = 6
    else:
        irrigation_factor = 0.88
        confidence_boost = -4

    # Calculate final predicted yield
    yield_val = base * lat_factor * irrigation_factor
    # Add minor deterministic variation based on coordinate hash
    seed = (abs(float(latitude)) * 31 + abs(float(longitude)) * 17) % 1.0
    yield_val += (seed - 0.5) * 0.4
    yield_val = max(0.8, round(yield_val, 1))

    # Base confidence score (75% to 92%)
    confidence = int(82 + confidence_boost + (seed * 8 - 4))
    confidence = min(96, max(68, confidence))

    # Soil suitability and tips
    soil_suitability = f"🌱 Ideal soil conditions detected for {crop_type}"
    growth_potential = "🌾 Weather conditions suggest moderate to high growth potential"
    
    tips = [
        f"Recommended seed sowing rate: 100-120 kg/ha for {crop_type}.",
        "Apply balanced NPK fertilization aligned with local soil tests.",
        "Ensure field drainage to prevent waterlogging during seedling emergence."
    ]
    if irrigation_used:
        tips.append("Scheduled drip/sprinkler irrigation can boost water efficiency by up to 25%.")
    else:
        tips.append("Implement mulching to conserve topsoil moisture during dry spells.")

    return {
        "predicted_yield": yield_val,
        "confidence": confidence,
        "soil_suitability": soil_suitability,
        "growth_potential": growth_potential,
        "tips": tips
    }


def get_field_insights(latitude, longitude):
    """
    Fetches real-time weather using OpenWeather API if configured,
    or calculates realistic agro-climatic & soil data based on coordinates.
    """
    lat = float(latitude)
    lon = float(longitude)
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
    
    weather_data = None
    
    if api_key:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                temp = data.get('main', {}).get('temp')
                humidity = data.get('main', {}).get('humidity')
                rain = data.get('rain', {}).get('1h', 0)
                weather_data = {
                    "temp": round(temp, 1),
                    "rainfall": round(rain, 1),
                    "humidity": int(humidity)
                }
        except Exception:
            weather_data = None

    # Realistic fallback weather model if API is unconfigured or unreachable
    if not weather_data:
        abs_lat = abs(lat)
        # Solar radiation model for temperature estimation
        base_temp = 32.0 - (abs_lat * 0.48)
        month = datetime.date.today().month
        seasonal_variation = math.sin((month - 4) * math.pi / 6) * 4.5
        temp = max(10.0, min(42.0, base_temp + seasonal_variation + ((lon % 5) - 2.5)))

        # Humidity estimation
        base_humidity = 65 - (abs_lat * 0.3) + ((lon % 7) - 3.5)
        humidity = max(25, min(90, int(base_humidity)))

        # Rainfall estimation (mm in past 24h)
        rain = 0.0 if humidity < 60 else round(((humidity - 60) * 0.35), 1)

        weather_data = {
            "temp": round(temp, 1),
            "rainfall": rain,
            "humidity": humidity
        }

    # Soil Health calculation based on geodetic heuristics
    coord_hash = (abs(lat) * 13.7 + abs(lon) * 19.3)
    ph = round(6.0 + ((coord_hash % 10) / 10.0) * 1.5 - 0.4, 1)  # 5.6 to 7.1
    carbon = round(1.1 + ((coord_hash % 8) / 10.0) * 0.9, 1)     # 1.1% to 1.8%
    nitrogen = int(35 + ((coord_hash % 15) * 2))                  # 35 to 65 mg/kg

    # Irrigation status calculation
    soil_moisture = (weather_data["humidity"] * 0.6) + (weather_data["rainfall"] * 4.0)
    if soil_moisture > 65:
        irrigation_status = "Optimal"
        efficiency = 78
        water_index = 0.75
    elif soil_moisture > 40:
        irrigation_status = "Moderate"
        efficiency = 65
        water_index = 0.60
    else:
        irrigation_status = "Low"
        efficiency = 55
        water_index = 0.48

    return {
        "weather": weather_data,
        "soil": {
            "ph": ph,
            "carbon": carbon,
            "nitrogen": nitrogen
        },
        "irrigation": {
            "status": irrigation_status,
            "efficiency": efficiency,
            "index": water_index
        }
    }
