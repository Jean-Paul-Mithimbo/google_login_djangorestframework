from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps

User = apps.get_model(settings.AUTH_USER_MODEL)

@receiver(post_save, sender=User)
def set_default_role(sender, instance, created, **kwargs):
    if created and not instance.role:
        instance.role = 'user'
        instance.save()
        