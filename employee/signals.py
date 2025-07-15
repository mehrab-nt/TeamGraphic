from django.db.models.signals import post_delete, post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import Employee, EmployeeLevel
from user.models import User


@receiver(pre_save, sender=Employee)
def employee_pre_save(sender, instance, **kwargs):
    """
    Clean employee data before save! (Ignore Changing User Data)
    """
    if instance.pk:
        try:
            old_employee = Employee.objects.get(pk=instance.pk)
        except Employee.DoesNotExist:
            return
        if old_employee.user != instance.user:
            instance.user = old_employee.user


@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance, created, **kwargs):
    """
    MEH: Clean Employee after save.
    like -> Set User model is_employee = True ...
    """
    if created:
        instance.user.is_employee = True
        instance.user.save(update_fields=['is_employee'])


@receiver(post_delete, sender=Employee)
def employee_post_delete(sender, instance, **kwargs):
    """
    MEH: Opposite direction Handle in on_delete.CASCADE() -> Change User Employee to Regular User!
    """
    try:
        instance.user.delete()
    except User.DoesNotExist:
        pass


@receiver(m2m_changed, sender=EmployeeLevel.api_items.through)
def clear_employee_level_api_keys_cache(sender, instance, **kwargs):
    cache_key = f"employee_level_api_keys:{instance.pk}"
    cache.delete(cache_key)
