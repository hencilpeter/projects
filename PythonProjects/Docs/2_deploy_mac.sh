#!/bin/bash
echo "================================"
echo "Django Deploy Script - macOS"
echo "================================"

# Unzip build
unzip -o django_build.zip -d app
cd app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Run server
python manage.py runserver 0.0.0.0:8000
