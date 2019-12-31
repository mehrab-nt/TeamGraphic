from django.db import models
# from django.utils import timezone


# class Delivery_Status(models.TextChoices):
#     Ready = 'rec', 'در حال ثبت'


class Delivery(models.Model):
    name = models.CharField(max_length=25)
    cost = models.IntegerField(default=0, blank=False)
    description = models.TextField(max_length=313, blank=True)
    duration = models.PositiveSmallIntegerField(default=0, blank=False)


# class Delivery(models.Model):
#     type = models.ForeignKey('Delivery_Type', on_delete=models.SET_NULL)
#     send_time = models.DateTimeField(blank=False, default=timezone.now)
