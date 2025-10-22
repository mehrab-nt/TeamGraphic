import django_filters
from .models import City


class CustomerFilter(django_filters.FilterSet):
    """
    MEH: Set filter for province on City List
    """
    class Meta:
        model = City
        fields = {
            'province': ['exact']
        }
