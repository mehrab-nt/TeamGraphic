from django.db import models
# from django.utils import timezone
from django.core import validators


# class Delivery_Status(models.TextChoices):
#     Ready = 'rec', 'در حال ثبت'


class Delivery(models.Model):
    name = models.CharField(max_length=25, validators=[validators.MinLengthValidator(3)])
    cost = models.IntegerField(default=0, blank=False, validators=[validators.MinValueValidator(0),
                                                                   validators.MaxValueValidator(99999999)])
    description = models.TextField(max_length=313, blank=True, validators=[validators.MinLengthValidator(10)])
    duration = models.PositiveSmallIntegerField(default=0, blank=False, validators=[validators.MinValueValidator(0),
                                                                                    validators.MaxValueValidator(10)])

    def __str__(self):
        return 'Delivery-{0}'.format(self.name)

    class Meta:
        verbose_name = 'ارسال ها'
        verbose_name_plural = 'ارسال ها'


# class Delivery(models.Model):
#     type = models.ForeignKey('Delivery_Type', on_delete=models.SET_NULL)
#     send_time = models.DateTimeField(blank=False, default=timezone.now)
