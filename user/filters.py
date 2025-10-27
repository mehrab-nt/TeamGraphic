import django_filters
from .models import User


class CustomerFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Customer on User List
    """
    default_province = django_filters.NumberFilter(
        method='filter_by_default_province',
        label='Province ID'
    )

    class Meta:
        model = User
        fields = {
            'id': ['exact'],
            'user_profile__job': ['contains'],
            'is_active': ['exact'],
            'phone_number_verified': ['exact'],
            'user_profile__gender': ['exact'],
            'role': ['exact'],
            'introduce_from': ['exact'],
            'date_joined': ['lte', 'gte'],
            'last_order_date': ['lte', 'gte'],
            'company__name': ['contains'],
        }

    @staticmethod
    def filter_by_default_province(queryset, name, value):
        """
        Filter users who have a default address with the given province ID
        """
        return queryset.filter(
            user_addresses__is_default=True,
            user_addresses__province_id=value
        )
