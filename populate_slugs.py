"""
Script to populate slugs for existing prompts
Run with: python populate_slugs.py
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commandvault.settings')
django.setup()

from vault.models import Prompt
from django.utils.text import slugify
import uuid

def populate_slugs():
    # Get all prompts without slugs
    prompts_without_slugs = Prompt.objects.filter(slug__isnull=True) | Prompt.objects.filter(slug='')
    total = prompts_without_slugs.count()
    
    print(f"Found {total} prompts without slugs")
    
    count = 0
    for prompt in prompts_without_slugs:
        base_slug = slugify(prompt.title)[:270]
        unique_suffix = str(uuid.uuid4())[:8]
        prompt.slug = f"{base_slug}-{unique_suffix}" if base_slug else f"prompt-{unique_suffix}"
        prompt.save()
        count += 1
        if count % 10 == 0:
            print(f"Processed {count}/{total} prompts...")
    
    print(f"✅ Successfully generated slugs for {count} prompts!")
    
    # Verify
    remaining = Prompt.objects.filter(slug__isnull=True).count() + Prompt.objects.filter(slug='').count()
    print(f"Prompts still without slugs: {remaining}")

if __name__ == '__main__':
    populate_slugs()
