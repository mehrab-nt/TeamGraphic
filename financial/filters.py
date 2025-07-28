import django_filters
from .models import Deposit


class DepositFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Deposit list
    """
    class Meta:
        model = Deposit
        fields = {
            'submit_date': ['lte', 'gte'],
            'deposit_type': ['exact'],
            'credit__owner__first_name': ['contains']
        }
