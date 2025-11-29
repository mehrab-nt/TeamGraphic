import django_filters
from .models import FileDirectory, FileItem


class TypeFilter(django_filters.FilterSet):
    """
    MEH: Set type filter for File Explorer
    """
    class Meta:
        model = FileItem
        fields = {
            'type': ['contains'],
        }
