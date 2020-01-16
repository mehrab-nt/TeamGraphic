from django.db import models
from django.utils import timezone
from django.core import validators


class PaymentType(models.TextChoices):
    CASH = 'csh', 'نقدی'
    POS = 'pos', 'کارتخوان'
    DEPOSIT = 'dep', 'واریز'
    GATEWAY = 'gwy', 'درگاه'


class Transaction(models.Model):
    record_date = models.DateTimeField(default=timezone.now, blank=False)
    confirm_date = models.DateTimeField(blank=True)
    type = models.CharField(max_length=3, choices=PaymentType.choices)
    amount = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(0),
                                                                  validators.MaxValueValidator(99999999)])
    confirm = models.BooleanField(default=False)
    order = models.ForeignKey('order.Order', on_delete=models.SET_NULL, null=True, blank=False,
                              related_name='order_transaction')
    record_user = models.ForeignKey('user.UserTG', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='user_transaction_record')

    def __str__(self):
        return 'تراکنش: {0}:{1}$'.format(self.type, self.amount)

    class Meta:
        verbose_name = 'تراکنش های مالی'
        verbose_name_plural = 'تراکنش های مالی'


class PrintingHouse(models.Model):
    id = models.CharField(max_length=2, primary_key=True, validators=[validators.MinLengthValidator(1)])
    title = models.CharField(max_length=20, validators=[validators.MinLengthValidator(1)])
    record_date = models.DateTimeField(default=timezone.now, blank=False)

    def __str__(self):
        return 'چاپخانه:{0}'.format(self.title)

    class Meta:
        verbose_name = 'چاپخانه ها'
        verbose_name_plural = 'چاپخانه ها'


class PrintingHousePayment(models.Model):
    record_date = models.DateTimeField(default=timezone.now, blank=False)
    order = models.ForeignKey('order.Order', on_delete=models.SET_NULL, null=True, blank=False,
                              related_name='payment_for_printing')
    printing_house = models.ForeignKey('PrintingHouse', on_delete=models.SET_NULL, null=True, blank=False,
                                       related_name='all_payment')
    record_user = models.ForeignKey('user.UserTG', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='user_record_print_payment')

    def __str__(self):
        return 'پرداختی به {0}'.format(self.printing_house)

    class Meta:
        verbose_name = 'پرداختی به چاپخانه'
        verbose_name_plural = 'پرداختی به چاپخانه'


class PrintingHouseIncome(models.Model):
    record_date = models.DateTimeField(default=timezone.now, blank=False)
    record_user = models.ForeignKey('user.UserTG', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='user_record_print_income')
    printing_house = models.ForeignKey('PrintingHouse', on_delete=models.SET_NULL, null=True, blank=False,
                                       related_name='all_income')

    def __str__(self):
        return 'دریافتی از {0}'.format(self.printing_house)

    class Meta:
        verbose_name = 'دریافتی از چاپخانه'
        verbose_name_plural = 'دریافتی از چاپخانه'


class FinancialType(models.Model):
    title = models.CharField(max_length=77, blank=False, unique=True, validators=[validators.MinLengthValidator(3)])
    mode = models.BooleanField(default=True)

    def __str__(self):
        return 'دریافت/پرداخت: {0}$'.format(self.title)

    class Meta:
        verbose_name = 'نوع پرداخت/دریافت'
        verbose_name_plural = 'نوع پرداخت/دریافت'


class Financial(models.Model):
    record_date = models.DateTimeField(default=timezone.now, blank=False)
    type = models.ForeignKey('FinancialType', on_delete=models.SET_NULL, null=True, blank=False,
                             related_name='financial_type')
    amount = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(0),
                                                                  validators.MaxValueValidator(99999999)])
    record_user = models.ForeignKey('user.UserTG', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='user_financial_record')

    def __str__(self):
        return '{0}:{1}$'.format(self.type, self.amount)

    class Meta:
        verbose_name = 'پرداخت/دریافت'
        verbose_name_plural = 'پرداخت/دریافت'


class Salary(models.Model):
    payment_date = models.DateTimeField(default=timezone.now, blank=False)
    record_user = models.ForeignKey('user.UserTG', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='user_salary_payment_record')
    for_user = models.ForeignKey('user.UserTG', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='user_salary')
    base_salary = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(0),
                                                                       validators.MaxValueValidator(99999999)])
    reduce_salary = models.PositiveIntegerField(default=0, blank=False,
                                                validators=[validators.MinValueValidator(0),
                                                            validators.MaxValueValidator(99999999)])
    amount = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(0),
                                                                  validators.MaxValueValidator(99999999)])

    def __str__(self):
        return 'حقوق {0}$'.format(self.for_user.user)

    class Meta:
        verbose_name = 'حقوق ها'
        verbose_name_plural = 'حقوق ها'


