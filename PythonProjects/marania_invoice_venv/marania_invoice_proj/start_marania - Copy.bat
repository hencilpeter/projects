@echo off
REM ---------------------------------------
REM Launch Django project with Waitress
REM ---------------------------------------

REM Go to project directory
cd /d "C:\Users\User\Documents\GitHub\PythonProjects\marania_invoice_venv\marania_invoice_proj"

REM Activate virtual environment
call "..\Scripts\activate"

REM Start Waitress server
start "Django Waitress" python -m waitress --listen=127.0.0.1:8000 marania_invoice_proj.wsgi:application

REM Wait for server to start
timeout /t 5 /nobreak > nul

REM Open Chrome
start "" chrome "http://127.0.0.1:8000"
