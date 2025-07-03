from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Role, User, UserProfile


# MEH: Lessen if default role remove! why?
@receiver(post_delete, sender=Role)
def assign_default_role_to_users(sender, instance, **kwargs):
    default_role = Role.objects.filter(is_default=True).first()
    if default_role:
        User.objects.filter(role__isnull=True, is_employee=False).update(role=default_role)


# MEH: Create profile for user automatically when a new user created ...
@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if not instance.user_profile:
        profile = UserProfile.objects.create()
        instance.user_profile = profile
        instance.save()


# MEH: If profile deleted in any way, User also deleted!!!
@receiver(post_delete, sender=User)
def delete_profile_after_delete_user(sender, instance, **kwargs):
    if instance.user_profile:
        instance.user_profile.delete()
