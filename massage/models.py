from django.db import models
from django.core import validators
from django.utils import timezone
from employee.models import Employee
from user.models import User, Role


class AlarmMassage(models.Model):
    title = models.CharField(max_length=26, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    content = models.TextField(max_length=236,
                               blank=False, null=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True,
                                 related_name='write_alarm_massage_list')
    start_date = models.DateTimeField(blank=False, null=False, verbose_name='Start Date')
    end_date = models.DateTimeField(blank=False, null=False, verbose_name='End Date')
    role = models.ForeignKey(Role, on_delete=models.PROTECT,
                             blank=True, null=True,
                             related_name='alarm_massage_list')

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Alarm Massage'
        verbose_name_plural = 'Alarms Massage'

    def __str__(self):
        return f'Alarm Massage: {self.title}'


class SmsMassage(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE,
                                 blank=False, null=False,
                                 related_name='sms_massage_list')
    counter = models.PositiveSmallIntegerField(default=1,
                                               blank=False, null=False)
    content = models.TextField(max_length=500,
                               blank=False, null=False)
    send_date = models.DateTimeField(default=timezone.now,
                                     blank=False, null=False, verbose_name='Send Date')
    tracking_code = models.CharField(max_length=23,
                                     blank=False, null=False, verbose_name='Tracking Code')
    panel = models.CharField(max_length=23,
                             blank=False, null=False)
    status = models.BooleanField(default=False,
                                 blank=False, null=False)

    class Meta:
        ordering = ['-send_date']
        verbose_name = 'SMS Massage'
        verbose_name_plural = 'SMS Massages'

    def __str__(self):
        return f'SmsMassage /For: {self.receiver.username}'


class Department(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    employees = models.ManyToManyField(
        Employee,
        through='DepartmentEmployee',
        through_fields=('department', 'employee')
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f'Department: {self.title}'


class DepartmentEmployee(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
                                   related_name='employee_list')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='department_list')

    class Meta:
        ordering = ['department']
        verbose_name = 'Department Employee'
        verbose_name_plural = 'Department Employees'

    def __str__(self):
        return f'{self.department} /For: {self.employee}'


class MassageStatus(models.TextChoices):
    NEW =  'NEW', 'جدید'
    ANSWERED = 'ANS', 'پاسخ داده شده'
    PENDING = 'PEN', 'در انتظار پاسخ'
    ORDER = 'ORD', 'ایجاد سفارش'
    SUBMITTED = 'SUB', 'ثبت سفارش'
    ENDED = 'END', 'بسته شده'


class WebMassage(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             blank=False, null=False,
                             related_name='web_massage_list')
    department = models.ForeignKey(Department, on_delete=models.PROTECT,
                                   blank=False, null=False,
                                   related_name='web_massage_list')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='web_massage_list')
    title = models.CharField(max_length=78, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    date = models.DateTimeField(default=timezone.now,
                                blank=False, null=False)
    file_access = models.BooleanField(default=False,
                                      blank=False, null=False)
    status = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                              choices=MassageStatus.choices, default=MassageStatus.NEW)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Web Massage'
        verbose_name_plural = 'Web Massages'

    def __str__(self):
        return f'Web Massage: {self.title}'


class MassageType(models.TextChoices):
    SEND = 'SEN', 'ارسال'
    RECEIVE = 'REC', 'دریافت'


class WebMassageContent(models.Model):
    content = models.TextField(max_length=500, validators=[validators.MinLengthValidator(3)],
                               blank=False, null=False)
    date = models.DateTimeField(default=timezone.now,
                                blank=False, null=False)
    parent = models.ForeignKey(WebMassage, on_delete=models.PROTECT,
                               blank=False, null=False,
                               related_name='content_list')
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=MassageType.choices, default=MassageType.SEND)
    # file = models.FileField(blank=False, null=False, upload_to=MassageType.SEND)

    class Meta:
        ordering = ['-date', 'parent']
        verbose_name = 'Web Massage'
        verbose_name_plural = 'Web Massages'

    def __str__(self):
        return f'Content: {self.pk} /For: {self.parent}'
