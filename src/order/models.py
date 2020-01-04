from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.core import validators
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
    cart_id = models.CharField(max_length=8, primary_key=True, validators=[validators.MinLengthValidator(8)])
    # user = models.ForeignKey('user.User', on_delete=models.CASCADE, blank=True, null=True,
    #                          related_name='user_carts')
    status = models.CharField(max_length=3, blank=False, choices=Cart_Status.choices, default=Cart_Status.Record)
    total_cost = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(1000),
                                                                      validators.MaxValueValidator(99999999)])
    delivery = models.ForeignKey('delivery.Delivery', on_delete=models.SET_NULL, null=True, blank=False,
                                 related_name='all_cart')
    create_date = models.DateTimeField(default=timezone.now, blank=False)
    duration = models.IntegerField(default=0, blank=False, validators=[validators.MinValueValidator(0),
                                                                       validators.MaxValueValidator(30)])
    delivery_date = models.DateField(blank=False, default=timezone.now)
    # payment

    def __str__(self):
        return 'Cart-{0}'.format(self.cart_id)


class Order(models.Model):
    order_id = models.CharField(max_length=8, primary_key=True, validators=[validators.MinLengthValidator(8)])
    cart = models.ForeignKey('Cart', on_delete=models.SET_NULL, null=True, blank=False,
                             related_name='cart_orders')
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=False,
                               related_name='sub_orders')
    # product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=False,
    #                             related_name='in_orders')
    design_feature = models.BooleanField(blank=False, default=False)
    count = models.IntegerField(default=1, blank=False, validators=[validators.MinValueValidator(1),
                                                                    validators.MaxValueValidator(10)])
    description = models.TextField(max_length=777, blank=True, validators=[validators.MinLengthValidator(10)])
    duration = models.IntegerField(default=0, blank=False, validators=[validators.MinValueValidator(0),
                                                                       validators.MaxValueValidator(30)])
    ready_date = models.DateField(blank=False)
    cost = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(1000),
                                                                validators.MaxValueValidator(99999999)])

    def __str__(self):
        return 'Order-{0}'.format(self.order_id)


class Type(models.TextChoices):
    Pos = 2, 'تایید'
    Neg = 0, 'لغو'
    Emp = 1, 'بررسی'


def status_vector_directory_path(instance, filename):
    return './order/static/img/status/{0}.png'.format(instance.status_id)


class Status(models.Model):
    status_id = models.CharField(max_length=3, primary_key=True, validators=[validators.MinLengthValidator(3)])
    title = models.CharField(max_length=20, blank=False, validators=[validators.MinLengthValidator(3)])
    # category
    vector = models.ImageField(upload_to=status_vector_directory_path, blank=False)
    type = models.CharField(max_length=1, choices=Type.choices, blank=False)

    def __str__(self):
        return '{0}'.format(self.title)


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
    if not old_vector == new_vector and old_vector:
        if os.path.isfile(old_vector.path):
            os.remove(old_vector.path)

