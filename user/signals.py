from django.db.models.signals import post_delete, post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.db.models import F
from django.core.cache import cache
from .models import Role, User, UserProfile, Introduction
from financial.models import Credit, CashBack


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    MEH: Clean User after save.
    like -> Create profile for user automatically when a new user created ...
    """
    flag = False
    if created:
        if not instance.user_profile:
            profile = UserProfile.objects.create()
            instance.user_profile = profile
            flag = True
        if not hasattr(instance, 'credit') and not instance.is_employee and not instance.is_staff :
            Credit.objects.create(owner=instance)
        if not instance.role and not instance.is_employee and not instance.is_staff:
            instance.role = Role.objects.filter(is_default=True).first()
            flag = True
        if instance.introduce_from:
            instance.introduce_from.number = F('number') + 1
            instance.introduce_from.save(update_fields=['number'])

    if getattr(instance, '_changed_introduce_from', False):
        if instance._original_introduce_from_id and instance._original_introduce_from_id != instance.introduce_from_id:
            Introduction.objects.filter(id=instance._original_introduce_from_id).update(number=F('number') - 1)
        if instance.introduce_from_id:
            Introduction.objects.filter(id=instance.introduce_from_id).update(number=F('number') + 1)

    if (instance.is_employee or instance.is_staff) and instance.role:
        if instance.role.cashback_active and getattr(instance.credit, "cashback", None):
            instance.credit.cashback.delete()
        instance.credit.delete()
        instance.role = None
        flag = True
    if not instance.is_staff and not instance.is_employee:
        if not instance.role:
            instance.role = Role.objects.filter(is_default=True).first()
            flag = True
        if not getattr(instance, "credit", None):
            Credit.objects.create(owner=instance)
        if instance.role.cashback_active and not getattr(instance.credit, "cashback", None):
            CashBack.objects.create(
                credit=instance.credit
            )
        elif not instance.role.cashback_active and getattr(instance.credit, "cashback", None):
            instance.credit.cashback.delete()
    if flag:
        instance.save()


@receiver(pre_save, sender=Role)
def role_pre_save(sender, instance, **kwargs):
    """
    MEH: Clean User with this Role before save.
    """
    if instance.pk:
        try:
            old_role = Role.objects.get(pk=instance.pk)
        except Role.DoesNotExist:
            return
        if old_role.cashback_active != instance.cashback_active:
            user_list = instance.role_all_users.select_related('credit').all()
            for user in user_list:
                if instance.cashback_active and not getattr(user.credit, 'cashback', None):
                    CashBack.objects.create(
                        credit=user.credit
                    )
                elif not instance.cashback_active and getattr(user.credit, 'cashback', None):
                    user.credit.cashback.delete()


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


@receiver(m2m_changed, sender=Role.api_items.through)
def clear_role_api_keys_cache(sender, instance, **kwargs):
    cache_key = f"role_api_keys:{instance.pk}"
    cache.delete(cache_key)
