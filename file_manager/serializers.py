from rest_framework import serializers
from .models import FileDirectory, FileItem, ClearFileHistory
from api.responses import *
from api.mixins import CustomModelSerializer
import jdatetime


class FileDirectorySerializer(CustomModelSerializer):
    """
    MEH: File Directory Full Information for file_explorer
    """
    type = serializers.SerializerMethodField()
    parent_directory = serializers.PrimaryKeyRelatedField(queryset=FileDirectory.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FileDirectory
        fields = ['id', 'name', 'create_date', 'type', 'parent_directory']

    @staticmethod
    def get_type(obj):
        return 'dir'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance and isinstance(instance, FileDirectory):
            self.fields['parent_directory'].queryset = FileDirectory.objects.exclude(pk=instance.pk)


class FileItemSerializer(CustomModelSerializer):
    """
    MEH: File Item Full Information for file_explorer
    (img width & height can set manually for final optimized image size if `seo_base = True`)
    """
    preview = serializers.ImageField(read_only=True)
    type = serializers.CharField(read_only=True)
    volume = serializers.FloatField(read_only=True)
    img_width = serializers.IntegerField(default=0, write_only=True)
    img_height = serializers.IntegerField(default=0, write_only=True)
    parent_directory = serializers.PrimaryKeyRelatedField(queryset=FileDirectory.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FileItem
        fields = ['id', 'name', 'preview', 'file', 'create_date', 'type', 'parent_directory', 'volume', 'seo_base', 'img_width', 'img_height']

    def validate(self, data): # MEH: Check uploaded Image size and Image -> SEO Base request (Optimize in filemanager.images.py)
        file = data.get('file')
        width = data.pop('img_width', 0)
        height = data.pop('img_height', 0)
        if file:
            size_mb = file.size / (1024 * 1024)
            if size_mb > 100: # todo: set max_size in some config for file manager (also for max_image_size)
                raise serializers.ValidationError(TG_MAX_FILE_SIZE + str(size_mb) + 'MB')
            seo_base = data.get('seo_base', False)
            if seo_base: # MEH: Change image to SEO base friendly format
                data['file'] = self.validate_upload_image(file, max_image_size=23, max_width=None, max_height=None, size=(width, height))
        return data


class ClearFileSerializer(CustomModelSerializer):
    """
    MEH: Clear File History full Information
    """
    year = serializers.IntegerField(required=True, allow_null=False, write_only=True)
    month = serializers.IntegerField(required=True, allow_null=False, write_only=True)
    employee = serializers.StringRelatedField()

    class Meta:
        model = ClearFileHistory
        fields = '__all__'
        read_only_fields = ['id', 'employee', 'from_date', 'until_date', 'submit_date', 'delete_number']

    def create(self, validated_data): # MEH: Change date to jalali and then submit delete old file request
        year = validated_data.pop('year')
        month = validated_data.pop('month')
        sh_first_day = jdatetime.date(year, month, 1)
        from_date = sh_first_day.togregorian()
        if month == 12 and not jdatetime.date(year, 1, 1).isleap():
            days_in_month = 29
        elif month <= 6:
            days_in_month = 31
        elif month <= 11:
            days_in_month = 30
        else:
            days_in_month = 30  # Esfand in leap year
        sh_last_day = jdatetime.date(year, month, days_in_month)
        until_date = sh_last_day.togregorian()
        history = ClearFileHistory.objects.create(
            from_date=from_date,
            until_date=until_date,
            employee=validated_data['employee'],
        )
        history.clear_order_files()
        return history
