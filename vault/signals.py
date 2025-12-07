from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Like, Comment, Follow, Notification

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created and instance.prompt.owner != instance.user:
        Notification.objects.create(
            user=instance.prompt.owner,
            notification_type='like',
            content=f"{instance.user.username} liked your prompt '{instance.prompt.title}'",
            related_prompt=instance.prompt,
            related_user=instance.user
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.prompt.owner != instance.user:
        Notification.objects.create(
            user=instance.prompt.owner,
            notification_type='comment',
            content=f"{instance.user.username} commented on your prompt '{instance.prompt.title}'",
            related_prompt=instance.prompt,
            related_user=instance.user
        )

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.following,
            notification_type='follow',
            content=f"{instance.follower.username} started following you",
            related_user=instance.follower
        )
