#!/usr/bin/env bash
set -e

pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput
python manage.py migrate --noinput

echo "Starting Gunicorn server..."
gunicorn commandvault.wsgi:application --bind 0.0.0.0:$PORT
