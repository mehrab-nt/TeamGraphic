from django.db import models
from django.utils import timezone


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


class Status(models.Model):
    status_id = models.CharField(max_length=3, primary_key=True)
    title = models.CharField(max_length=20, blank=False)
    # category
    vector = models.ImageField(blank=False)
    type = models.CharField(max_length=1, choices=Type.choices, blank=False)
