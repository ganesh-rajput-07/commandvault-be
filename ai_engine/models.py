from django.db import models
from django.utils.translation import gettext_lazy as _

class AIProvider(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., OpenAI, Midjourney")
    base_url = models.URLField(help_text="API Base URL (e.g., https://api.openai.com/v1)")
    api_key = models.CharField(max_length=255, help_text="Securely stored API Key")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AIModel(models.Model):
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100, help_text="Display Name (e.g., DALL-E 3)")
    api_id = models.CharField(max_length=100, help_text="Model ID expected by the API (e.g., dall-e-3)")
    version = models.CharField(max_length=50, blank=True, null=True, help_text="Optional version string")
    is_active = models.BooleanField(default=True)
    
    # Configuration for default parameters (JSON)
    default_params = models.JSONField(default=dict, blank=True, help_text="Default generation parameters")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('provider', 'api_id')

    def __str__(self):
        return f"{self.name} ({self.provider.name})"
