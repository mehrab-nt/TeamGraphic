import django_filters
from .models import SmsMessage, WebMessage


class SmsMessageFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Sms message list
    """
    class Meta:
        model = SmsMessage
        fields = {
            'send_date': ['lte', 'gte'],
            'success': ['exact'],
        }


class WebMessageFilter(django_filters.FilterSet):
    """
    MEH: Set some filter for Web message list
    """
    class Meta:
        model = WebMessage
        fields = {
            'create_date': ['lte', 'gte'],
            'status': ['exact'],
            'type': ['exact'],
            'title': ['contains']
        }
