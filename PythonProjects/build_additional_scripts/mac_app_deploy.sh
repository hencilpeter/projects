#!/bin/bash

APP_DIR="$(cd "$(dirname "$0")/../app" && pwd)"

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating venv..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r "$APP_DIR/requirements.txt"

echo "Copying the scripts..."
cp /source/path/deploy_windows.bat /target/path/build/scripts/
cp /source/path/deploy_mac.sh /target/path/build/scripts/

echo "Applying migrations..."
cd "$APP_DIR"
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django (dev server)..."
python manage.py runserver 0.0.0.0:8000
