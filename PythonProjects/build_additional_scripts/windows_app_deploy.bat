@echo off
set APP_DIR=.\app

echo Creating virtual environment...
python -m venv venv

echo Activating venv...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r %APP_DIR%\requirements.txt

mkdir %APP_DIR%\static


echo Applying migrations...
cd %APP_DIR%
python manage.py migrate

echo Collecting static files...
python manage.py collectstatic --noinput

echo Deployment Completed.....
REM echo Starting Django using Waitress...
REM waitress-serve --listen=0.0.0.0:8005 marania_invoice_proj.wsgi:application

pause
