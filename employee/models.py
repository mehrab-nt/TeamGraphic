from django.db import models
from django.core import validators
from user.models import User
from api.models import ApiItem


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='employee_profile')
    level = models.ForeignKey("EmployeeLevel", on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name="employee_list")
    rate = models.FloatField(default=5,
                             blank=False, null=False)

    class Meta:
        ordering = ['-user__date_joined']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f'Employee: {self.user.first_name} {self.user.last_name}'


class EmployeeLevel(models.Model):
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                blank=True, null=True,
                                related_name="employee_levels_create")
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=300,
                                   blank=True, null=True)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name="Is Active")
    api_items = models.ManyToManyField(ApiItem, verbose_name="Api Items", blank=True,
                                       related_name="employee_levels")

    class Meta:
        verbose_name = "Employee Level"
        verbose_name_plural = "Employee Levels"

    def __str__(self):
        return f'Employee Level: {self.title}'
