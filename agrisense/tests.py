import json
from django.test import TestCase, Client
from .models import PredictionRecord, FieldInsightRecord

class AgriSenseTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_page_loads(self):
        """Test home page loads successfully with 200 OK."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AgriSense')
        self.assertContains(response, 'Crop Yield Prediction')

    def test_predict_endpoint_post(self):
        """Test crop yield prediction calculation & DB persistence."""
        payload = {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "crop_type": "Wheat",
            "planting_date": "2026-11-20",
            "irrigation": True
        }
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertGreater(data.get('predicted_yield', 0), 0)
        self.assertGreaterEqual(data.get('confidence', 0), 50)
        self.assertIn('tips', data)

        # Verify record was created in database
        self.assertEqual(PredictionRecord.objects.count(), 1)
        rec = PredictionRecord.objects.first()
        self.assertEqual(rec.crop_type, 'Wheat')
        self.assertTrue(rec.irrigation_used)

    def test_predict_endpoint_flask_keys(self):
        """Test backwards compatibility with Flask parameter names."""
        payload = {
            "lat": 31.1471,
            "lon": 75.3412,
            "crop": "Rice",
            "date": "2026-11-20",
            "irrigation": False
        }
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data.get('predicted_yield', 0), 0)

    def test_insights_endpoint(self):
        """Test agro-climatic & soil insights calculation & DB persistence."""
        payload = {
            "latitude": 28.6139,
            "longitude": 77.2090
        }
        response = self.client.post(
            '/insights',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('weather', data)
        self.assertIn('soil', data)
        self.assertIn('irrigation', data)

        # Verify record was created in database
        self.assertEqual(FieldInsightRecord.objects.count(), 1)

    def test_history_endpoint(self):
        """Test prediction history retrieval API."""
        PredictionRecord.objects.create(
            latitude=20.0,
            longitude=75.0,
            crop_type="Maize",
            planting_date="2026-11-20",
            irrigation_used=True,
            predicted_yield=6.2,
            confidence=88
        )
        response = self.client.get('/api/history/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('history', data)
        self.assertGreaterEqual(len(data['history']), 1)
