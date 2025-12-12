from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.contrib.auth import get_user_model
import random
import string

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


def generate_random_username():
    """Generate a random username in format CV-USER-xxxxx"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    username = f'CV-USER-{random_suffix}'
    
    # Ensure username is unique
    while User.objects.filter(username=username).exists():
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        username = f'CV-USER-{random_suffix}'
    
    return username


def get_or_create_google_user(idinfo):
    email = idinfo.get('email')
    google_id = idinfo.get('sub')
    name = idinfo.get('name', '')
    given_name = idinfo.get('given_name', '')
    family_name = idinfo.get('family_name', '')

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': generate_random_username(),
            'first_name': given_name,
            'last_name': family_name,
            'google_id': google_id,
            'is_google_account': True
        }
    )
    return user
