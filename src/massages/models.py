from django.db import models
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Employee


class SmsMassage(models.Model):
    tracking_code = models.CharField(max_length=23, blank=False, null=False, verbose_name="Tracking Code")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False,
                                 related_name='user_sms_massages')
    receiver_number = models.CharField(max_length=11, validators=[validators.MinLengthValidator(11)],
                                       blank=False, null=False, verbose_name="Receiver Number")
    counter = models.PositiveSmallIntegerField(default=1, blank=False, null=False, verbose_name="Counter")
    content = models.TextField(max_length=300, blank=False, null=False)
    send_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    panel = models.CharField(max_length=23, blank=False, null=False)
    status = models.BooleanField(default=False, blank=False, null=False)

    class Meta:
        ordering = ['-send_date']
        verbose_name = 'SMS Massage'
        verbose_name_plural = 'SMS Massages'


class Department(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    employees = models.ManyToManyField(
        Employee,
        through='EmployeeDepartment',
        through_fields=('department', 'employee')
    )


class EmployeeDepartment(models.Model):
    department = models.ForeignKey('Department', on_delete=models.PROTECT,
                                   related_name='all_employee')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                 related_name='all_department')


class MassageStatus(models.TextChoices):
    NEW = 'جدید'
    ANSWERED = 'پاسخ داده شده'
    WAITING = 'در انتظار پاسخ'
    CLOSED = 'بسته شده'


class WebMassage(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False,
                             related_name='user_web_massages')
    department = models.ForeignKey('Department', on_delete=models.PROTECT, blank=False, null=False,
                                   related_name='all_web_massage')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=False, null=False,
                                 related_name='employee_web_massage')
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    file_access = models.BooleanField(default=False, blank=False, null=False)
    status = models.CharField(max_length=14, choices=MassageStatus.choices, default=MassageStatus.NEW)


class MassageType(models.TextChoices):
    SEND = "ارسال"
    RECEIVE = "دریافت"


class WebMassageContent(models.Model):
    content = models.TextField(max_length=300, blank=False, null=False)
    date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    parent = models.ForeignKey('WebMassage', on_delete=models.PROTECT, blank=False, null=False,
                               related_name='contents')
    type = models.CharField(max_length=6, choices=MassageType.choices, default=MassageType.SEND)
    # file = models.FileField(blank=False, null=False, upload_to=MassageType.SEND)


