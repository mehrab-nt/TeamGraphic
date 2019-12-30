from django.db import models
from django.utils import timezone


class User(models.Model):
    mobile = models.CharField(primary_key=True, max_length=11, verbose_name='Mobile Number')
    password = models.CharField(max_length=20)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    confirm_code = models.CharField(max_length=4, null=True)
    email = models.CharField(blank=True, max_length=50)
    Profile = models.ImageField(default=0, blank=True, verbose_name='Profile Image')
    # point = models.IntegerField(default=0)
    reg_time = models.DateTimeField(default=timezone.now)
    last_edit_time = models.DateTimeField(auto_now=True)
    # intro_code
    # inv_code


class Country(models.TextChoices):
    IRAN = 'IRI', 'ایران'


class State(models.TextChoices):
    TEHRAN = 'TEH', 'تهران'


class Address(models.Model):
    country = models.CharField(max_length=3, choices=Country.choices, default=Country.IRAN)
    state = models.CharField(max_length=3, choices=State.choices, default=State.TEHRAN)
    # city =
    # area = just for tehran
    detail = models.CharField(max_length=313, verbose_name='Address')
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name='user_addresses')


class Delivery(models.Model):
    type = models.ForeignKey('Delivery_Type', on_delete=models.SET_NULL)


class Delivery_Type(models.Model):
    name = models.CharField(max_length=25)
    # cost =
    # TODO: here

class Cart(models.Model):
    cart_id = models.CharField(max_length=8, primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name='user_carts', blank=True, null=True)
    status = models.ForeignKey('Cart_Status', on_delete=models.SET_NULL, null=True, blank=False)
    cost = models.PositiveIntegerField(default=-1, blank=False)
    delivery = models.ForeignKey('Delivery', on_delete=models.SET_NULL, null=True, blank=False,
                                 related_name='all_cart')
    # payment


class Order(models.Model):
    order_id = models.CharField(max_length=10, primary_key=True)
    cart = models.ForeignKey('Cart', on_delete=models.SET_NULL, null=True, blank=False,
                             related_name='cart_orders')
    status = models.ForeignKey('Order_Status', on_delete=models.SET_NULL, null=True, blank=False,
                               related_name='sub_orders')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=False,
                                related_name='in_orders')
    count = models.IntegerField(default=1, blank=False)
    description = models.TextField(max_length=777, blank=True)
    create_date = models.DateTimeField(default=timezone.now, blank=False)
    duration = models.IntegerField(default=0, blank=False)
    ready_date = models.DateField(blank=False)
    cost = models.IntegerField(default=-1, blank=False)



    # count = models.IntegerField(default=1)
