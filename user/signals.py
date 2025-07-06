from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.db.models import F
from .models import Role, User, UserProfile


@receiver(post_delete, sender=Role)
def role_post_delete(sender, instance, **kwargs):
    """
    MEH: Lessen if default role remove! why?
    """
    default_role = Role.objects.filter(is_default=True).first()
    if default_role:
        User.objects.filter(role__isnull=True, is_employee=False).update(role=default_role)


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    MEH: Clean User after save.
    like -> Create profile for user automatically when a new user created ...
    """
    flag = False
    if not instance.user_profile:
        profile = UserProfile.objects.create()
        instance.user_profile = profile
        flag = True
    if not instance.role and not instance.is_employee and not instance.is_staff:
        instance.role = Role.objects.filter(is_default=True).first()
        flag = True
    if instance.is_employee and instance.role:
        instance.role = None
        flag = True
    if instance.introduce_from:
        if created:
            instance.introduce_from.number = F('number') + 1
            instance.introduce_from.save(update_fields=['number'])
    if flag:
        instance.save()


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """
    Clean user data before save!
    """
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
        except User.DoesNotExist:
            return
        if old_user.introduce_from != instance.introduce_from:
            if old_user.introduce_from:
                old_user.introduce_from.number = F('number') + 1
                old_user.introduce_from.save(update_fields=['number'])
            if instance.introduce_from:
                instance.introduce_from.number = F('number') + 1
                instance.introduce_from.save(update_fields=['number'])


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    """
    MEH: Mines introduce counter by 1 & If User deleted in any way, profile also deleted!!!
    (Opposite direction Handle in on_delete.CASCADE()
    """
    if instance.introduce_from:
        instance.introduce_from.number = F('number') - 1
        instance.introduce_from.save(update_fields=['number'])
    try:
        instance.user_profile.delete()
    except UserProfile.DoesNotExist:
        pass
