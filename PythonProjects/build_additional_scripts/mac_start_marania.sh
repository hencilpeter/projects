#!/bin/bash
# ---------------------------------------
# Launch Django + Waitress
# Auto-stop when Chrome fully exits
# ---------------------------------------

APP_DIR="$HOME/Documents/GitHub/PythonProjects/marania_invoice_venv/marania_invoice_proj"
VENV_DIR="$HOME/Documents/GitHub/PythonProjects/marania_invoice_venv"

cd "$APP_DIR" || exit 1

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Starting Django (Waitress)..."
python -m waitress --listen=127.0.0.1:8000 marania_invoice_proj.wsgi:application &
WAITRESS_PID=$!

sleep 5

echo "Launching Chrome..."
open -a "Google Chrome" "http://127.0.0.1:8000"

echo "Waiting for Chrome to close..."

# ---- Wait until Chrome is fully closed ----
while pgrep -x "Google Chrome" > /dev/null; do
    sleep 2
done

echo "Chrome closed. Stopping Django..."
kill $WAITRESS_PID

echo "Django stopped."
exit 0
