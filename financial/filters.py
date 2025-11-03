import django_filters
from .models import Deposit


class DepositFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Deposit list
    """
    user = django_filters.NumberFilter(field_name='credit__owner__id', lookup_expr='exact')
    employee = django_filters.NumberFilter(field_name='submit_by', lookup_expr='exact')

    class Meta:
        model = Deposit
        fields = {
            'submit_date': ['lte', 'gte'],
            'deposit_type': ['exact'],
            'transaction_type': ['exact'],
            'online_status': ['exact'],
            'bank': ['exact'],
            'tracking_code': ['contains'],
        }
