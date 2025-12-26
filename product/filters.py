import django_filters
from .models import Product, OptionCategory


class ProductReportFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Product sale Report
    """
    class Meta:
        model = Product
        fields = {
            'total_order': ['lte', 'gte'],
            'last_order': ['lte', 'gte'],
            'total_main_sale': ['lte', 'gte'],
            'total_option_sale': ['lte', 'gte'],
        }


class OptionFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Option type
    """
    class Meta:
        model = OptionCategory
        fields = {
            'option_type': ['exact'],
        }
