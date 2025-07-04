from django.contrib import admin
from .models import Employee, EmployeeLevel, EmployeeLevelAccessApiItem


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'rate']


class EmployeeLevelAccessApiItemInline(admin.TabularInline):
    model = EmployeeLevelAccessApiItem
    extra = 1
    autocomplete_fields = ['api_item']


class EmployeeLevelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_active', 'manager', 'description']
    inlines = [EmployeeLevelAccessApiItemInline]


class EmployeeLevelAccessApiItemAdmin(admin.ModelAdmin):
    list_display = ('employee_level', 'api_item')


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeLevel, EmployeeLevelAdmin)
admin.site.register(EmployeeLevelAccessApiItem, EmployeeLevelAccessApiItemAdmin)
