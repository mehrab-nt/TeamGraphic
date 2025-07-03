import django_filters
from .models import Employee


class EmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = Employee
        fields = {
            'user__first_name': ['contains'],
            'rate': ['gte', 'lte'],
        }
