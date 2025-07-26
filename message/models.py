from django.db import models
from django.core import validators
from django.utils import timezone
from employee.models import Employee
from user.models import User, Role


class AlarmMessage(models.Model):
    title = models.CharField(max_length=26, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    content = models.TextField(max_length=236,
                               blank=False, null=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True,
                                 related_name='write_alarm_message_list')
    start_date = models.DateTimeField(blank=False, null=False, verbose_name='Start Date')
    end_date = models.DateTimeField(blank=False, null=False, verbose_name='End Date')
    role = models.ForeignKey(Role, on_delete=models.PROTECT,
                             blank=True, null=True,
                             related_name='alarm_message_list')

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Alarm Message'
        verbose_name_plural = 'Alarms Message'

    def __str__(self):
        return f'Alarm Message: {self.title}'


class SmsMessage(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE,
                                 blank=False, null=False,
                                 related_name='sms_message_list')
    number = models.PositiveSmallIntegerField(default=1,
                                              blank=False, null=False)
    content = models.TextField(max_length=500,
                               blank=False, null=False)
    send_date = models.DateTimeField(auto_now=True,
                                     blank=False, null=False, verbose_name='Send Date')
    tracking_code = models.CharField(max_length=23,
                                     blank=False, null=False, verbose_name='Tracking Code')
    panel = models.CharField(max_length=23,
                             blank=False, null=False)

    class Meta:
        ordering = ['send_date']
        verbose_name = 'SMS Message'
        verbose_name_plural = 'SMS Messages'

    def __str__(self):
        return f'SmsMessage /For: {self.receiver.username}'


class Department(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    employees = models.ManyToManyField(Employee, blank=True,
                                       related_name='department_list')

    class Meta:
        ordering = ['title']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f'Department: {self.title}'


class MessageStatus(models.TextChoices):
    NEW =  'NEW', 'جدید'
    ANSWERED = 'ANS', 'پاسخ داده شده'
    PENDING = 'PEN', 'در انتظار پاسخ'
    ORDER = 'ORD', 'ایجاد سفارش'
    SUBMITTED = 'SUB', 'ثبت سفارش'
    ENDED = 'END', 'بسته شده'


class WebMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             blank=False, null=False,
                             related_name='web_message_list')
    department = models.ForeignKey(Department, on_delete=models.PROTECT,
                                   blank=False, null=False,
                                   related_name='web_message_list')
    title = models.CharField(max_length=78, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    date = models.DateTimeField(default=timezone.now,
                                blank=False, null=False)
    file_access = models.BooleanField(default=False,
                                      blank=False, null=False)
    status = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                              choices=MessageStatus.choices, default=MessageStatus.NEW)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Web Message'
        verbose_name_plural = 'Web Messages'

    def __str__(self):
        return f'Web Message: {self.title}'


class MessageType(models.TextChoices):
    SEND = 'SEN', 'ارسال'
    RECEIVE = 'REC', 'دریافت'

def user_message_upload_path(instance, filename): # MEH: Store file in media in user folder (it's not in file manager!)
    return f'user/messages/{instance.user.id}-{filename}'

class WebMessageContent(models.Model):
    content = models.TextField(max_length=500, validators=[validators.MinLengthValidator(3)],
                               blank=False, null=False)
    date = models.DateTimeField(auto_now=True,
                                blank=False, null=False)
    parent = models.ForeignKey(WebMessage, on_delete=models.PROTECT,
                               blank=False, null=False,
                               related_name='content_list')
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=MessageType.choices, default=MessageType.RECEIVE)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='web_message_list')
    file = models.FileField(upload_to=user_message_upload_path, blank=True, null=True)

    class Meta:
        ordering = ['-date', 'parent']
        verbose_name = 'Web Message'
        verbose_name_plural = 'Web Messages'

    def __str__(self):
        return f'Content: {self.pk} /For: {self.parent}'
