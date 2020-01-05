from django.db import models
from django.utils import timezone
from django.core import validators


class PaymentType(models.TextChoices):
    CASH = 'csh', 'نقدی'
    POS = 'pos', 'کارتخوان'
    DEPOSIT = 'dep', 'واریز'
    GATEWAY = 'gwy', 'درگاه'


class Financial(models.Model):
    record_date = models.DateTimeField(default=timezone.now, blank=False)
    confirm_date = models.DateTimeField(blank=True)
    type = models.CharField(max_length=3, choices=PaymentType.choices)
    amount = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(0),
                                                                  validators.MaxValueValidator(99999999)])
    confirm = models.BooleanField(default=False)
    order = models.ForeignKey('order.Order', on_delete=models.SET_NULL, null=True, blank=False,
                              related_name='order_payments')
    record_user = models.ForeignKey('user.UserTG', on_delete=models.SET_NULL, null=True, blank=False,
                                    related_name='user_payments_record')

    def __str__(self):
        return '{0}:{1}$'.format(self.type, self.amount)
