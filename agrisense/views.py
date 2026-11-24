import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PredictionRecord, FieldInsightRecord
from .services import calculate_crop_prediction, get_field_insights

def index_view(request):
    """Renders the main AgriSense interactive dashboard."""
    recent_predictions = PredictionRecord.objects.all()[:10]
    return render(request, 'agrisense/index.html', {
        'recent_predictions': recent_predictions
    })

@csrf_exempt
def predict_view(request):
    """
    POST /predict or /api/predict/
    Accepts both {lat, lon, crop, date, irrigation} and {latitude, longitude, crop_type, planting_date, irrigation}
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        # Support both 'lat'/'latitude', 'lon'/'longitude', 'crop'/'crop_type'
        lat_val = data.get('lat') if 'lat' in data else data.get('latitude', 28.6139)
        lon_val = data.get('lon') if 'lon' in data else data.get('longitude', 77.2090)
        crop_val = data.get('crop') if 'crop' in data else data.get('crop_type', 'Wheat')
        date_val = data.get('date') if 'date' in data else data.get('planting_date', '2026-11-20')
        irrigation_val = data.get('irrigation', False)

        latitude = float(lat_val)
        longitude = float(lon_val)
        crop_type = str(crop_val).strip()
        planting_date = str(date_val).strip()
        irrigation_used = True if str(irrigation_val).lower() in ['true', '1', 'on'] or irrigation_val is True else False

        if not crop_type or crop_type == 'Select crop':
            return JsonResponse({"error": "Please select a valid crop type."}, status=400)

        # Run prediction calculation
        result = calculate_crop_prediction(
            latitude=latitude,
            longitude=longitude,
            crop_type=crop_type,
            planting_date=planting_date,
            irrigation_used=irrigation_used
        )

        # Persist to Django database (SQLite)
        record = PredictionRecord.objects.create(
            latitude=latitude,
            longitude=longitude,
            crop_type=crop_type,
            planting_date=planting_date or '2026-11-20',
            irrigation_used=irrigation_used,
            predicted_yield=result["predicted_yield"],
            confidence=result["confidence"],
            soil_suitability=result["soil_suitability"],
            growth_potential=result["growth_potential"],
            tips=result["tips"]
        )

        # Format tips matching both original UI and enhanced UI
        all_tips = [result["soil_suitability"], result["growth_potential"]] + result["tips"]

        response_data = {
            "success": True,
            "id": record.id,
            "predicted_yield": result["predicted_yield"],
            "confidence": result["confidence"],
            "soil_suitability": result["soil_suitability"],
            "growth_potential": result["growth_potential"],
            "tips": all_tips,
            "created_at": record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        return JsonResponse(response_data)

    except (ValueError, TypeError) as e:
        return JsonResponse({"error": f"Invalid input parameters: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)


@csrf_exempt
def insights_view(request):
    """
    POST /insights or /api/insights/
    Returns weather, soil health, and irrigation metrics for coordinates.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        lat_val = data.get('lat') if 'lat' in data else data.get('latitude')
        lon_val = data.get('lon') if 'lon' in data else data.get('longitude')

        if lat_val is None or lon_val is None or str(lat_val).strip() == '' or str(lon_val).strip() == '':
            return JsonResponse({"error": "Latitude and longitude are required."}, status=400)

        latitude = float(lat_val)
        longitude = float(lon_val)

        # Fetch insights
        insights = get_field_insights(latitude, longitude)

        # Persist to database
        FieldInsightRecord.objects.create(
            latitude=latitude,
            longitude=longitude,
            temperature=insights["weather"]["temp"],
            rainfall=insights["weather"]["rainfall"],
            humidity=insights["weather"]["humidity"],
            soil_ph=insights["soil"]["ph"],
            organic_carbon=insights["soil"]["carbon"],
            nitrogen=insights["soil"]["nitrogen"],
            irrigation_status=insights["irrigation"]["status"],
            irrigation_efficiency=insights["irrigation"]["efficiency"],
            water_index=insights["irrigation"]["index"]
        )

        # Structure response to be compatible with both original and enhanced UIs
        w_temp = insights["weather"]["temp"]
        w_rain = insights["weather"]["rainfall"]
        w_hum = insights["weather"]["humidity"]
        s_ph = insights["soil"]["ph"]
        s_carb = insights["soil"]["carbon"]
        s_nitr = insights["soil"]["nitrogen"]
        i_stat = insights["irrigation"]["status"]
        i_eff = insights["irrigation"]["efficiency"]
        i_idx = insights["irrigation"]["index"]

        response_payload = {
            "weather": {
                "temp": f"{w_temp}°C",
                "temp_val": w_temp,
                "rain": f"{w_rain}mm",
                "rainfall": w_rain,
                "humidity": f"{w_hum}%",
                "humidity_val": w_hum
            },
            "soil": {
                "ph": f"{s_ph}",
                "carbon": f"{s_carb}%",
                "carbon_val": s_carb,
                "nitrogen": f"{s_nitr} mg/kg",
                "nitrogen_val": s_nitr
            },
            "irrigation": {
                "status": f"{i_stat}",
                "efficiency": f"{i_eff}%",
                "efficiency_val": i_eff,
                "index": f"{i_idx}",
                "index_val": i_idx
            }
        }

        return JsonResponse(response_payload)

    except ValueError:
        return JsonResponse({"error": "Invalid coordinates provided."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Internal error: {str(e)}"}, status=500)


def history_view(request):
    """GET /api/history/ - Returns recent prediction records."""
    records = PredictionRecord.objects.all()[:15]
    data = []
    for r in records:
        data.append({
            "id": r.id,
            "crop": r.crop_type,
            "lat": r.latitude,
            "lon": r.longitude,
            "yield": r.predicted_yield,
            "confidence": r.confidence,
            "date": r.created_at.strftime('%b %d, %Y %H:%M')
        })
    return JsonResponse({"history": data})
