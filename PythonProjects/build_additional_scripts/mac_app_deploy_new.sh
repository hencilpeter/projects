#!/bin/bash

set -e  # Exit immediately if a command fails

APP_DIR="./app"

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating venv..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"

echo "Creating static directory..."
mkdir -p "$APP_DIR/static"

echo "Applying migrations..."
cd "$APP_DIR"
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Deployment Completed."
read -p "Press Enter to exit..."
