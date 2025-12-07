from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        return idinfo
    except Exception:
        return None


def get_or_create_google_user(idinfo):
    email = idinfo.get('email')
    google_id = idinfo.get('sub')
    name = idinfo.get('name', '')

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0],
            'google_id': google_id,
            'is_google_account': True
        }
    )
    return user
