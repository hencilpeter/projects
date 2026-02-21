#!/bin/bash

# ---------------------------------------
# Launch Django + Waitress
# Auto-stop server when Chrome exits
# ---------------------------------------

set -e

APP_DIR="./app"

echo "Changing to app directory..."
cd "$APP_DIR"

echo "Activating virtual environment..."
source "../venv/bin/activate"

echo "Starting Waitress..."
python -m waitress --listen=127.0.0.1:8000 marania_invoice_proj.wsgi:application &
WAITRESS_PID=$!

sleep 5

echo "Launching Google Chrome..."
open -a "Google Chrome" "http://127.0.0.1:8000"

echo "Waiting for Chrome to close..."
while pgrep -x "Google Chrome" > /dev/null; do
    sleep 2
done

echo "Chrome closed. Stopping Waitress..."
kill "$WAITRESS_PID"

echo "Server stopped."
exit 0
