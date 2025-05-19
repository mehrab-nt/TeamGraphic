from django.db import models


class CoinStatus(models.TextChoices):
    ACTIVE = 'act'
    EXPIRED = 'exp'
    USED = 'use'


class Company(models.Model):
    company_name = models.CharField(max_length=25, blank=False, null=False, unique=True)
    national_number = models.CharField(max_length=11, blank=True, null=True, unique=True)
    economic_number = models.CharField(max_length=11, blank=True, null=True, unique=True)
    reg_number = models.CharField(max_length=11, blank=True, null=True, unique=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    address_text = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    accounting_id = models.IntegerField(blank=False, null=False)


class Credit(models.Model):
    credit_amount = models.IntegerField(blank=False, null=False)
    tmp_cashback = models.IntegerField(blank=False, null=False)
    # tmp_cashback_set_date =
    cashback = models.IntegerField(blank=False, null=False)
    total_coin = models.IntegerField(blank=False, null=False)


class Coin(models.Model):
    base_coin_amount = models.IntegerField(blank=False, null=False)
    now_coin_amount = models.IntegerField(blank=False, null=False)
    coin_description = models.TextField(blank=False, null=False)
    reg_date = models.DateField(blank=False, null=False)
    exp_date = models.DateField(blank=False, null=False)
    status = models.CharField(max_length=3, choices=CoinStatus.choices, default=CoinStatus.ACTIVE,
                              blank=False, null=False)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, blank=False, null=False)

