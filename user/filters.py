import django_filters
from rest_framework import filters
from .models import User


class CustomerQueryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(is_employee=False)


class CustomerFilter(django_filters.FilterSet):
    default_province = django_filters.NumberFilter(field_name='default_province_id', lookup_expr='exact', label='Province id')

    class Meta:
        model = User
        fields = {
            'first_name': ['contains'],
            'user_profile__job': ['contains'],
            'is_active': ['exact'],
            'user_profile__gender': ['exact'],
            'role': ['exact'],
            'date_joined': ['lte', 'gte'],
            'last_order_date': ['lte', 'gte'],
        }
