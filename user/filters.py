import django_filters
from .models import User


class CustomerFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Customer on User List
    """
    default_province = django_filters.NumberFilter(field_name='default_province_id', lookup_expr='exact', label='Province id')

    class Meta:
        model = User
        fields = {
            'user_profile__job': ['contains'],
            'is_active': ['exact'],
            'phone_number_verified': ['exact'],
            'user_profile__gender': ['exact'],
            'role': ['exact'],
            'date_joined': ['lte', 'gte'],
            'last_order_date': ['lte', 'gte'],
        }
