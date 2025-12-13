from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    is_google_account = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)  # Keep for Google avatars
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)  # YouTube-style banner
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    is_email_public = models.BooleanField(default=False)
    profile_updated_at = models.DateTimeField(auto_now=True)
    
    # Email Verification Fields
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def soft_delete(self):
        self.is_active = False
        self.save()
    
    def is_verification_token_valid(self):
        """Check if verification token is still valid (24 hours)"""
        if not self.email_verification_sent_at:
            return False
        expiry_time = self.email_verification_sent_at + timezone.timedelta(hours=24)
        return timezone.now() < expiry_time
