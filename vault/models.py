from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Prompt(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prompts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, blank=True, db_index=True)  # Not unique to avoid migration issues
    text = models.TextField()
    ai_model = models.JSONField(default=list, blank=True, help_text="AI models/tools used (e.g., ['ChatGPT-4', 'Claude'])")
    example_output = models.TextField(blank=True, help_text="Example output from this prompt")
    
    # Media outputs
    output_image = models.ImageField(upload_to='prompt_outputs/images/', blank=True, null=True, help_text="Example image output")
    output_video = models.FileField(upload_to='prompt_outputs/videos/', blank=True, null=True, help_text="Example video output")
    output_audio = models.FileField(upload_to='prompt_outputs/audio/', blank=True, null=True, help_text="Example audio output")
    output_type = models.CharField(max_length=20, blank=True, choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('code', 'Code'),
    ], help_text="Type of output example")
    
    tags = models.JSONField(default=list, blank=True)
    use_case = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    times_used = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    save_count = models.IntegerField(default=0)
    trend_score = models.FloatField(default=0.0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', 'is_public']),
            models.Index(fields=['is_public', '-trend_score']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from title with ID for uniqueness
            base_slug = slugify(self.title)[:270]
            # Add a short random suffix for uniqueness
            unique_suffix = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_suffix}" if base_slug else f"prompt-{unique_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class PromptVersion(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='versions')
    old_text = models.TextField()
    old_title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"v{self.id} of {self.prompt_id}"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'prompt')
        indexes = [models.Index(fields=['user', 'prompt'])]

    def __str__(self):
        return f"{self.user.username} likes {self.prompt.title}"

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['prompt', '-created_at'])]

    def __str__(self):
        return f"{self.user.username} on {self.prompt.title}"

class SavedPrompt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_prompts')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'prompt')
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'])]

    def __str__(self):
        return f"{self.user.username} saved {self.prompt.title}"

class PromptView(models.Model):
    """Track when users view prompts (open detail modal)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prompt_views')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='viewed_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'prompt')
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'prompt'])]

    def __str__(self):
        return f"{self.user.username} viewed {self.prompt.title}"

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [models.Index(fields=['follower', 'following'])]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    related_prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, null=True, blank=True)
    related_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='triggered_notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read', '-created_at'])]

    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"

class Report(models.Model):
    REPORT_STATUS = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    )
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', '-created_at'])]

    def __str__(self):
        return f"Report by {self.reporter.username} on {self.prompt.title}"