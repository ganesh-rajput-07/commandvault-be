"""
WSGI config for commandvault project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promptdeck.settings')

application = get_wsgi_application()


# Serve static files on Vercel
from whitenoise import WhiteNoise
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Serve static files
static_root = str(BASE_DIR / 'staticfiles')
if not os.path.exists(static_root):
    try:
        os.makedirs(static_root)
    except OSError:
        pass
application = WhiteNoise(application, root=static_root)
app = application

