@echo off
echo ================================
echo Django Deploy Script - WINDOWS
echo ================================

REM Unzip build
powershell Expand-Archive django_build.zip -DestinationPath app -Force
cd app

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM Apply migrations
python manage.py migrate

REM Collect static files
python manage.py collectstatic --noinput

REM Start server
python manage.py runserver 0.0.0.0:8000

pause
