from django.contrib import admin
from .models import Employee, EmployeeLevel
from api.models import ApiItem


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'rate']


class EmployeeLevelAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'manager', 'description']
    filter_horizontal = ['api_items']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'api_items':
            kwargs["queryset"] = ApiItem.objects.filter(category__role_base=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeLevel, EmployeeLevelAdmin)
