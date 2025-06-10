import django_filters
from rest_framework import filters
from .models import User


class CustomerFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(is_employee=False)


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'first_name': ['exact', 'contains'],
        }
