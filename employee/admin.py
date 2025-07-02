from django.contrib import admin
from .models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'rate']


admin.site.register(Employee, EmployeeAdmin)
