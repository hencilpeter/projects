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
xcopy /E /I /Y your_project build\your_project
xcopy /E /I /Y your_app build\your_app
copy manage.py build\
copy requirements.txt build\
copy db.sqlite3 build\  REM (Only if SQLite)

REM Exclude unnecessary files
rmdir /s /q build\venv
rmdir /s /q build\__pycache__

REM Zip build folder
powershell Compress-Archive -Path build\* -DestinationPath django_build.zip -Force

echo ================================
echo Build completed: django_build.zip
echo ================================
pause
