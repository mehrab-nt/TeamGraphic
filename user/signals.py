from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Role, User, UserProfile


@receiver(post_delete, sender=Role)
def assign_default_role_to_users(sender, instance, **kwargs):
    default_role = Role.objects.filter(is_default=True).first()
    if default_role:
        User.objects.filter(role__isnull=True).update(role=default_role)


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
