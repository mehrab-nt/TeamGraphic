from django.db import models
from django.utils import timezone
from user.models import User
from employee.models import Employee
from order.models import Order, Cart


class UserReport(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE,
                                    blank=False, null=False,
                                    related_name='report')
    total_order = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Total Order')
    first_order_price = models.PositiveIntegerField(default=0, blank=False, null=False,
                                                    verbose_name='First Order Price')
    first_order_date = models.DateField(blank=True, null=True, verbose_name='First Order Date')
    first_seller_employee = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                              blank=True, null=True, verbose_name='First Seller Employee',
                                              related_name='customer_list')
    last_order_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Last Order Price')
    last_order_date = models.DateField(blank=True, null=True, verbose_name='Last Order Date')
    total_product_buy = models.PositiveIntegerField(default=0, blank=False, null=False,
                                                    verbose_name='Total Product Buy')
    total_option_buy = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Total Option Buy')

    class Meta:
        ordering = ['last_order_date']
        verbose_name = 'User Report'
        verbose_name_plural = 'User Reports'

    def __str__(self):
        return f'Report: {self.customer}'


class DailySaleReport(models.Model):
    date = models.DateField(default=timezone.now,
                            blank=False, null=False)
    total_product_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Product Income')
    total_options_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Option Income')
    sale_counter = models.PositiveIntegerField(blank=False, null=False, verbose_name='Sale Counter')
    total_delivery_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Delivery Income')
    total_discount = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Discount')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Daily Sale Report'
        verbose_name_plural = 'Daily Sale Reports'

    def __str__(self):
        return f'Daily Sale Report: {self.date}'


class MonthlySaleReport(models.Model):
    month = models.PositiveSmallIntegerField(blank=False, null=False)
    year = models.PositiveSmallIntegerField(blank=False, null=False)
    total_product_income = models.PositiveBigIntegerField(blank=False, null=False, verbose_name='Total Product Income')
    total_options_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Option Income')
    sale_counter = models.PositiveIntegerField(blank=False, null=False, verbose_name='Sale Counter')
    total_delivery_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Delivery Income')
    total_discount = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Discount')

    class Meta:
        ordering = ['-month', '-year']
        verbose_name = 'Monthly Sale Report'
        verbose_name_plural = 'Monthly Sale Reports'

    def __str__(self):
        return f'Monthly Sale Report: {self.month} - {self.year}'


class CounterReport(models.Model):
    user_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='User Number')
    product_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Product Number')
    message_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Massage Number')
    new_order_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Order Number')
    ongoing_order_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Ongoing Order Number')
    ready_order_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Ready Order Number')

    class Meta:
        verbose_name = 'Counter Report'
        verbose_name_plural = 'Counter Reports'


class NotifReport(models.Model):
    pending_deposit = models.PositiveIntegerField(blank=False, null=False, verbose_name='Pending Deposit')
    inbox = models.PositiveIntegerField(blank=False, null=False, verbose_name='Inbox')
    price_ask = models.PositiveIntegerField(blank=False, null=False, verbose_name='Price Ask')
    new_cart = models.PositiveIntegerField(blank=False, null=False, verbose_name='Cart')
    new_user = models.PositiveIntegerField(blank=False, null=False, verbose_name='New User')
    delivery_request = models.PositiveIntegerField(blank=False, null=False, verbose_name='Delivery Request')
    agency_request = models.PositiveIntegerField(blank=False, null=False, verbose_name='Agency Request')
    inventory_alert = models.PositiveIntegerField(blank=False, null=False, verbose_name='Inventory Alert')
    incomplete_cart = models.PositiveIntegerField(blank=False, null=False, verbose_name='Incomplete Cart')

    class Meta:
        verbose_name = 'Notif Report'
        verbose_name_plural = 'Notif Reports'
