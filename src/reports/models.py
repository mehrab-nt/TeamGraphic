from django.db import models
from django.utils import timezone


class DailySaleReport(models.Model):
    date = models.DateField(default=timezone.now, blank=False, null=False)
    total_product_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Product Income')
    total_options_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Option Income')
    sale_counter = models.PositiveIntegerField(blank=False, null=False, verbose_name='Sale Counter')
    total_delivery_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Delivery Income')
    total_discount = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Discount Sale')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Daily Sale Report'
        verbose_name_plural = 'Daily Sale Reports'


class MonthlySaleReport(models.Model):
    month = models.PositiveSmallIntegerField(blank=False, null=False)
    year = models.PositiveSmallIntegerField(blank=False, null=False)
    total_product_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Product Income')
    total_options_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Option Income')
    sale_counter = models.PositiveIntegerField(blank=False, null=False, verbose_name='Sale Counter')
    total_delivery_income = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Delivery Income')
    total_discount = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Discount Sale')

    class Meta:
        ordering = ['-month', '-year']
        verbose_name = 'Monthly Sale Report'
        verbose_name_plural = 'Monthly Sale Reports'


class CounterReport(models.Model):
    user_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='User Number')
    product_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Product Number')
    massage_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Massage Number')
    new_order_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Order Number')
    ongoing_order_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Ongoing Order Number')
    ready_order_number = models.PositiveIntegerField(blank=False, null=False, verbose_name='Ready Order Number')

    class Meta:
        verbose_name = 'Counter Report'
        verbose_name_plural = 'Counter Reports'