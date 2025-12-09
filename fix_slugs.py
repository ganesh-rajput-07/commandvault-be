"""
Quick fix: Update all prompts to have slugs
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commandvault.settings')
django.setup()

from vault.models import Prompt
from django.utils.text import slugify
import uuid

# Update ALL prompts to ensure they have proper slugs
all_prompts = Prompt.objects.all()
print(f"Updating {all_prompts.count()} prompts...")

for prompt in all_prompts:
    # Force regenerate slug for all
    base_slug = slugify(prompt.title)[:270]
    unique_suffix = str(uuid.uuid4())[:8]
    prompt.slug = f"{base_slug}-{unique_suffix}" if base_slug else f"prompt-{unique_suffix}"
    prompt.save(update_fields=['slug'])
    print(f"Updated: {prompt.id} -> {prompt.slug}")

print("✅ Done!")
