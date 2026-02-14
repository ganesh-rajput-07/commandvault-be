#!/bin/bash
# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

# Apply database migrations
echo "Applying database migrations..."
python3 manage.py migrate

echo "Build completed."
