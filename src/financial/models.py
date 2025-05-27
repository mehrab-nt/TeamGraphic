from django.db import models
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=25, blank=False, null=False, unique=True)
    national_number = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name='National number')
    economic_number = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name='Economic number')
    reg_number = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name='Reg Number')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Postal Code')
    state = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    address_content = models.TextField(blank=True, null=True, verbose_name='Address Content')
    phone_number = models.CharField(max_length=12, blank=True, null=True, verbose_name='Phone Number')
    accounting_id = models.PositiveBigIntegerField(blank=False, null=False, verbose_name='Accounting ID')

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"Company: {self.name}"


class Credit(models.Model):
    credit_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Credit Amount')
    tmp_cashback = models.PositiveIntegerField(blank=False, null=False, verbose_name='Tmp Cashback')
    # tmp_cashback_set_date =
    cashback = models.PositiveIntegerField(blank=False, null=False)
    total_coin = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Coin')

    class Meta:
        verbose_name = 'Credit'
        verbose_name_plural = 'Credits'

    def __str__(self):
        return f"Credit: {self.credit_user}"


class CoinStatus(models.TextChoices):
    ACTIVE = 'فعال'
    EXPIRED = 'منقضی'
    USED = 'استفاده شده'


class Coin(models.Model):
    base_coin_amount = models.IntegerField(blank=False, null=False, verbose_name='Base Coin Amount')
    now_coin_amount = models.IntegerField(blank=False, null=False, verbose_name='Now Coin Amount')
    description = models.TextField(blank=False, null=False)
    reg_date = models.DateField(default=timezone.now, blank=False, null=False, verbose_name='Reg Date')
    exp_date = models.DateField(blank=False, null=False, verbose_name='Exp Date')
    status = models.CharField(max_length=12, choices=CoinStatus.choices, default=CoinStatus.ACTIVE,
                              blank=False, null=False)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='coin_list')

    class Meta:
        verbose_name = 'Coin'
        verbose_name_plural = 'Coins'

    def __str__(self):
        return f"Coin #{self.base_coin_amount} for {self.credit}"
