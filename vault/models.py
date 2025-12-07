from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


def __str__(self):
    return self.name


class Prompt(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    tags = models.JSONField(default=list, blank=True) # list of strings
    use_case = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    times_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# PostgreSQL full-text index
    search_vector = SearchVectorField(null=True, editable=False)


    class Meta:
        indexes = [GinIndex(fields=['search_vector'])]


    def __str__(self):
        return self.title


class PromptVersion(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='versions')
    old_text = models.TextField()
    old_title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"v{self.id} of {self.prompt_id}"