from django.db import models
from django.utils import timezone
from django.dispatch import receiver
import os


class Cart_Status(models.TextChoices):
    Record = 'rec', 'در حال ثبت'
    Check = 'chk', 'در حال بررسی'
    Preparation = 'pre', 'آماده سازی'
    Ready = 'rdy', 'آماده تحویل'
    Delivery = 'del', 'آماده ارسال'
    Sending = 'snd', 'ارسال شد'
    Get = 'get', 'تحویل داده شد'
    Cancel = 'can', 'لغو شده'
    Remaining = 'rem', 'صورت حساب مانده'


class Cart(models.Model):
    cart_id = models.CharField(max_length=8, primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE,
                             related_name='user_carts', blank=True, null=True)
    status = models.CharField(max_length=3, blank=False, choices=Cart_Status.choices, default=Cart_Status.Record)
    total_cost = models.PositiveIntegerField(blank=False)
    delivery = models.ForeignKey('delivery.Delivery', on_delete=models.SET_NULL, null=True, blank=False,
                                 related_name='all_cart')
    create_date = models.DateTimeField(default=timezone.now, blank=False)
    duration = models.IntegerField(default=0, blank=False)
    delivery_date = models.DateField(blank=False, default=timezone.now)
    # payment


class Order(models.Model):
    order_id = models.CharField(max_length=10, primary_key=True)
    cart = models.ForeignKey('Cart', on_delete=models.SET_NULL, null=True, blank=False,
                             related_name='cart_orders')
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=False,
                               related_name='sub_orders')
    # product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=False,
    #                             related_name='in_orders')
    design_feature = models.BooleanField(blank=False, default=False)
    count = models.IntegerField(default=1, blank=False)
    description = models.TextField(max_length=777, blank=True)
    duration = models.IntegerField(default=0, blank=False)
    ready_date = models.DateField(blank=False)
    cost = models.PositiveIntegerField(blank=False)


class Type(models.TextChoices):
    Pos = 2, 'تایید'
    Neg = 0, 'لغو'
    Emp = 1, 'بررسی'


def status_vector_directory_path(instance, filename):
    return './order/static/img/status/{0}.png'.format(instance.status_id)


class Status(models.Model):
    status_id = models.CharField(max_length=3, primary_key=True)
    title = models.CharField(max_length=20, blank=False)
    # category
    vector = models.ImageField(upload_to=status_vector_directory_path, blank=False)
    type = models.CharField(max_length=1, choices=Type.choices, blank=False)


@receiver(models.signals.post_delete, sender=Status)
def auto_delete_status_on_delete(sender, instance, **kwargs):
    if instance.vector:
        if os.path.isfile(instance.vector.path):
            os.remove(instance.vector.path)


@receiver(models.signals.pre_save, sender=Status)
def auto_delete_template_file_on_change(sender, instance, **kwargs):
    if not instance.status_id:
        return False
    try:
        old_vector = Status.objects.get(pk=instance.status_id).vector
    except Status.DoesNotExist:
        return False
    new_vector = instance.vector
    if not old_vector == new_vector:
        if os.path.isfile(old_vector.path):
            os.remove(old_vector.path)

