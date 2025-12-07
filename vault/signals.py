from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Prompt, PromptVersion

@receiver(pre_save, sender=Prompt)
def update_search_and_version(sender, instance, **kwargs):
    # if updating existing prompt, save version
    if instance.pk:
        try:
            old = Prompt.objects.get(pk=instance.pk)
            if old.text != instance.text or old.title != instance.title:
                PromptVersion.objects.create(prompt=old, old_text=old.text, old_title=old.title)
        except Prompt.DoesNotExist:
            pass
    # update search vector
    combined = (instance.title or '') + ' ' + (instance.text or '') + ' ' + ' '.join(instance.tags or [])
    instance.search_vector = SearchVector('title', weight='A') + SearchVector('text', weight='B')
