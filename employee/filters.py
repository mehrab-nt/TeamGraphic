import django_filters
from .models import Employee, EmployeeLevel


class EmployeeFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Employee Api
    """
    class Meta:
        model = Employee
        fields = {
            'user__first_name': ['contains'],
            'level__title': ['contains'],
            'rate': ['gte', 'lte'],
        }


class EmployeeLevelFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Employee Level Api
    """
    class Meta:
        model = EmployeeLevel
        fields = {
            'is_active': ['exact'],
        }
