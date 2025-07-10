from rest_framework import serializers
from django.core.validators import RegexValidator
from landing.models import Landing
from .models import FileDirectory, FileItem
from api.responses import *
from api.mixins import CustomModelSerializer, CustomChoiceField
from django.utils import timezone
from .images import *


class FileDirectorySerializer(CustomModelSerializer):
    """
    MEH: File Directory Full Information for file_explorer
    """
    type = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    create_date = serializers.DateField(default=timezone.now(), read_only=True)

    class Meta:
        model = FileDirectory
        fields = ['id', 'name', 'preview', 'create_date', 'type']

    @staticmethod
    def get_type(obj):
        return 'dir'

    @staticmethod
    def get_preview(obj):
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance and isinstance(instance, FileDirectory):
            self.fields['parent_category'].queryset = FileDirectory.objects.exclude(pk=instance.pk)

    def validate_parent_directory(self, value): # MEH: Prevent from loop Directory A->B->C->A
        instance = self.instance
        if not instance or not value:
            return value
        current = value
        while current:
            if current == instance:
                raise serializers.ValidationError(TG_PREVENT_CIRCULAR_CATEGORY)
            current = current.parent_directory
        return value


class FileItemSerializer(CustomModelSerializer):
    """
    MEH: File Item Full Information for file_explorer
    (img width & height can set manually for final optimized image size if `seo_base = True`)
    """
    name = serializers.CharField(read_only=True)
    preview = serializers.ImageField(read_only=True)
    create_date = serializers.DateField(default=timezone.now(), read_only=True)
    type = serializers.CharField(read_only=True)
    volume = serializers.FloatField(read_only=True)
    img_width = serializers.IntegerField(default=0, write_only=True)
    img_height = serializers.IntegerField(default=0, write_only=True)

    class Meta:
        model = FileItem
        fields = ['id', 'name', 'preview', 'file', 'create_date', 'type', 'volume', 'seo_base', 'img_width', 'img_height']

    def validate(self, data): # MEH: Check uploaded Image size and Image -> SEO Base request (Optimize in filemanager.images.py)
        file = data.get('file')
        width = data.pop('img_width') or 0
        height = data.pop('img_height') or 0
        if file:
            size_mb = file.size / (1024 * 1024)
            if size_mb > 100:
                raise serializers.ValidationError(TG_MAX_FILE_SIZE + str(size_mb) + 'MB')
            seo_base = data.get('seo_base', False)
            if seo_base:
                data['file'] = self.validate_upload_image(file, max_image_size=23, max_width=None, max_height=None, size=(width, height))
        return data
