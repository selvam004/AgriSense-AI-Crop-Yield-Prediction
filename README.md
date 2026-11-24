# 🌾 AgriSense – AI Crop Yield Prediction (Django Edition)

An AI-driven precision agriculture dashboard designed to assist farmers, researchers, and agronomists in forecasting crop yield and monitoring agro-climatic conditions.

Originally built in Flask, this project has been completely rebuilt as an end-to-end **Django 5** web application with full SQLite database persistence, an interactive admin portal, and backwards compatibility with all existing endpoints.

---

## ✨ Features

- **🌾 AI Crop Yield Prediction Engine:**  
  Calculates expected crop yield in tons/hectare (`t/ha`) and confidence percentage based on crop type (Wheat, Rice, Maize, Soybean), GPS coordinates (latitude/longitude), planting seasonality, and irrigation status.
- **🌦️ Real-Time Field Insights:**  
  Delivers weather overview (temperature, rainfall, humidity), soil health metrics (pH, organic carbon %, nitrogen mg/kg), and irrigation diagnostics (efficiency %, water index).
  * Supports live **OpenWeather API** integration.
  * Includes a built-in deterministic agro-climatic estimation engine so it runs seamlessly even without an external API key or internet access!
- **💾 Full Django Database Persistence:**  
  Every prediction and field insight query is automatically persisted in an SQLite database via Django ORM models (`PredictionRecord`, `FieldInsightRecord`).
- **⚙️ Django Admin Portal:**  
  A pre-configured admin panel at `/admin/` to view, filter, search, and export farmer prediction records and field logs.
  * **Default Username:** `admin`
  * **Default Password:** `admin123`
- **📊 Real-Time History View:**  
  The interactive dashboard contains a live table displaying recent predictions stored in the database.
- **🎨 Modern Glassmorphic UI:**  
  Custom CSS animations, ambient gradient mesh background, responsive grid layout, and Google Font (Poppins).
- **🧪 Comprehensive Test Suite:**  
  Pre-written unit tests verifying all endpoints and database operations (`python manage.py test`).

---

## 🚀 Quick Start (How to Run in Local System)

### **Option 1: One-Click Launcher (Recommended)**

#### On Windows:
Double-click `run.bat` or open PowerShell/Command Prompt and run:
```cmd
run.bat
```

#### On Linux / macOS:
Open terminal, make the script executable, and run:
```bash
chmod +x run.sh
./run.sh
```

---

### **Option 2: Manual Step-by-Step Installation**

#### 1. Prerequisites
Ensure you have **Python 3.10+** installed. Check via:
```bash
python --version
```

#### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run Migrations & Seed Data
```bash
python manage.py migrate
```
*(The bundled `db.sqlite3` already includes the migration tables and the `admin` account).*

#### 5. Start the Development Server
```bash
python manage.py runserver
```

#### 6. Open in Your Browser
- **Main Web Application:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin Portal:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - **Username:** `admin`
  - **Password:** `admin123`

---

## 📡 API Endpoints

| Method | Endpoint | Description | Sample Payload |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Main interactive dashboard | None |
| `POST` | `/predict` | Predict crop yield and save record | `{"latitude": 28.61, "longitude": 77.20, "crop_type": "Wheat", "planting_date": "2026-11-20", "irrigation": true}` |
| `POST` | `/insights` | Fetch weather, soil & irrigation | `{"latitude": 28.61, "longitude": 77.20}` |
| `GET` | `/api/history/` | Get latest 15 prediction records | None |
| `GET` | `/admin/` | Django Administration Panel | (Admin login required) |

*Note: The endpoints accept both the original Flask keys (`lat`, `lon`, `crop`, `date`, `irrigation`) and full descriptive keys (`latitude`, `longitude`, `crop_type`, `planting_date`).*

---

## 🛠️ Project Structure

```text
agrisense_django/
├── agrisense/                  # Core Django application
│   ├── admin.py                # Admin panel registrations & customizations
│   ├── apps.py                 # App configuration
│   ├── models.py               # PredictionRecord & FieldInsightRecord models
│   ├── services.py             # ML yield prediction & agro-climatic engine
│   ├── tests.py                # Automated unit tests
│   ├── urls.py                 # API and view routes
│   └── views.py                # View controllers and API handlers
├── agrisense_project/          # Django project settings & WSGI configuration
│   ├── settings.py             # App settings, static files, database config
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # Production WSGI application
├── static/                     # Static assets
│   ├── css/
│   │   └── styles.css          # Full stylesheet with animations & glassmorphism
│   └── js/
│       └── app.js              # Client-side API interactions & UI updates
├── templates/
│   └── agrisense/
│       └── index.html          # Main application template
├── db.sqlite3                  # Pre-configured SQLite database with admin user
├── manage.py                   # Django CLI utility
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows 1-click launcher
├── run.sh                      # Linux/Mac 1-click launcher
└── README.md                   # Complete documentation
```

---

## 🧪 Running Automated Tests

Run the test suite at any time to verify application integrity:
```bash
python manage.py test
```
All 5 tests will execute and validate endpoint responses, prediction calculations, and database records.

---

## 📄 License
Crafted with care by **AgriSense AI** • Powered by Django 5, OpenWeather, Smart AI, and Sustainable Tech.
