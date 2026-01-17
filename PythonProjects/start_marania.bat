@echo off
REM ---------------------------------------
REM Launch Django + Waitress
REM Auto-close when Chrome fully exits
REM ---------------------------------------

cd /d "C:\Users\User\Documents\GitHub\PythonProjects\marania_invoice_venv\marania_invoice_proj"
call "..\Scripts\activate"

REM Start Waitress
start "Django Waitress" cmd /k python -m waitress --listen=127.0.0.1:8000 marania_invoice_proj.wsgi:application

timeout /t 5 /nobreak > nul

REM Launch Chrome
start "" chrome "http://127.0.0.1:8000"

REM ---- Wait until Chrome is fully closed ----
:WAIT_CHROME
tasklist | find /i "chrome.exe" >nul
if not errorlevel 1 (
    timeout /t 2 >nul
    goto WAIT_CHROME
)

REM Stop Waitress after Chrome closes
taskkill /FI "WINDOWTITLE eq Django Waitress*" /T /F

exit
