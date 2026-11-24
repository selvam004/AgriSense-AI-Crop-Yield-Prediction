#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  Starting AgriSense - AI Crop Yield Prediction (Django)"
echo "========================================================"
echo ""

# Check python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+."
    exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment (venv)..."
    python3 -m venv venv
fi

# Activate venv
echo "[*] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[*] Installing required packages..."
pip install -r requirements.txt --quiet

# Run database migrations
echo "[*] Checking database migrations..."
python manage.py migrate --noinput

echo ""
echo "========================================================"
echo "  AgriSense is ready!"
echo "  * Main Dashboard: http://127.0.0.1:8000/"
echo "  * Admin Portal:   http://127.0.0.1:8000/admin/"
echo "  * Admin User:     admin"
echo "  * Admin Password: admin123"
echo "========================================================"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

python manage.py runserver 0.0.0.0:8000
