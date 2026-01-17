@echo off
echo ================================
echo Django Build Script - SOURCE
echo ================================

REM Activate virtual environment
call venv\Scripts\activate

REM Freeze dependencies
pip freeze > requirements.txt

REM Collect static files
python manage.py collectstatic --noinput

REM Optional: run migrations check
REM python manage.py makemigrations
REM python manage.py migrate

REM Create build directory
if exist build rmdir /s /q build
mkdir build

REM Copy project files
xcopy /E /I /Y marania_invoice_proj build\marania_invoice_app
xcopy /E /I /Y marania_invoice_app build\marania_invoice_app
copy manage.py build\
copy requirements.txt build\
copy db.sqlite3 build\  REM (Only if SQLite)

REM Exclude unnecessary files
REM rmdir /s /q build\venv
REM rmdir /s /q build\__pycache__

REM Zip build folder
powershell Compress-Archive -Path build\* -DestinationPath marania_automation.zip -Force

echo ================================
echo Build completed: marania_automation.zip
echo ================================
pause
