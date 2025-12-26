#!/bin/bash
python manage.py migrate
gunicorn commandvault.wsgi:application
