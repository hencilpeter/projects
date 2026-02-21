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

pause
