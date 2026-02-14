#!/bin/bash

# Vercel Build Script
# This script handles all necessary steps to build the Django application on Vercel.

set -e  # Exit strictly on error

echo "🚀 Starting Vercel Build Process..."

# 1. Install Dependencies (Handled automatically by Vercel)
# echo "📦 Installing Requirements..."
# pip install -r requirements.txt

# 2. Database Migrations
# Note: Vercel functions are serverless and ephemeral. 
# It is generally recommended to use an external database (Supabase, Neon, AWS RDS, etc.)
# If you are using SQLite (default), the db.sqlite3 file will be reset on every deployment.
echo "🔄 Running Migrations..."
python manage.py migrate

# 3. Collect Static Files
echo "🎨 Collecting Static Files..."
python manage.py collectstatic --noinput


echo "✅ Build Completed Successfully!"