from django.db import models
from django.core import validators
from employee.models import Employee
from user.models import Role

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
                             related_name="alarm_massage_list")

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Alarm Massage"
        verbose_name_plural = "Alarms Massage"

    def __str__(self):
        return f"Alarm Massage: {self.title}"
