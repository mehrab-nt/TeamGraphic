from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from .models import Employee
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
