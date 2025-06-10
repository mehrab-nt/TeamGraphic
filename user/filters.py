import django_filters
from rest_framework import filters
from .models import User


class CustomerQueryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(is_employee=False)


class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'first_name': ['contains'],
        }
