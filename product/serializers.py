from rest_framework import serializers
from django.core.validators import RegexValidator
from file_manager.models import FileItem
from landing.models import Landing
from .models import Product, ProductType, ProductCategory, GalleryCategory, ProductStatus, TemplateFile, CountingUnit, \
    RoundPriceType
from api.responses import *
from api.mixins import CustomModelSerializer, CustomChoiceField


class ProductCategoryBriefSerializer(CustomModelSerializer):
    """
    MEH: Product Category Brief Information for product_explorer
    """
    type = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'title', 'status', 'sort_number', 'type', 'has_children']

    @staticmethod
    def get_type(obj):
        return 'CAT'

    @staticmethod
    def get_has_children(obj):
        return obj.sub_categories.exists()


class ProductBriefSerializer(CustomModelSerializer):
    """
    MEH: Product Brief Information for product_explorer
    """
    class Meta:
        model = Product
        fields = ['id', 'title', 'status', 'sort_number', 'type']


class ProductCategorySerializer(CustomModelSerializer):
    """
    MEH: Main Product Category full Information
    """
    title = serializers.CharField(required=True, min_length=3, max_length=78)
    description = serializers.CharField(default=None, allow_null=True, style={'base_template': 'textarea.html'})
    parent_category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), required=False, allow_null=True)
    parent_category_display = serializers.StringRelatedField(source='parent_category')
    image = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='webp', seo_base=True), required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    icon = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='svg'), required=False, allow_null=True)
    icon_url = serializers.StringRelatedField(source='icon')
    video = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='mkv'), required=False, allow_null=True)
    video_url = serializers.StringRelatedField(source='video')
    gallery = serializers.PrimaryKeyRelatedField(queryset=GalleryCategory.objects.all(), required=False, allow_null=True)
    status = CustomChoiceField(choices=ProductStatus.choices, initial=ProductStatus.ACTIVE, default=ProductStatus.ACTIVE)
    accounting_id = serializers.IntegerField(default=None,
                                             validators=[RegexValidator(regex=r'^\d{1,16}$', message=TG_DATA_WRONG)])
    counting_unit = CustomChoiceField(choices=CountingUnit.choices, initial=CountingUnit.TIRAGE, default=CountingUnit.TIRAGE)
    round_price = CustomChoiceField(choices=RoundPriceType.choices, initial=RoundPriceType.DEF, default=RoundPriceType.DEF)
    is_landing = serializers.BooleanField(default=False)
    landing = serializers.PrimaryKeyRelatedField(queryset=Landing.objects.all(), required=False, allow_null=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and obj.image.file:
            url = obj.image.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_icon_url(self, obj):
        request = self.context.get('request')
        if obj.icon and obj.icon.file:
            url = obj.icon.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video and obj.video.file:
            url = obj.video.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance and isinstance(instance, ProductCategory):
            self.fields['parent_category'].queryset = ProductCategory.objects.exclude(pk=instance.pk)

    def validate_parent_category(self, value): # MEH: Prevent from loop Category A->B->C->A
        instance = self.instance
        if not instance or not value:
            return value
        current = value
        while current:
            if current == instance:
                raise serializers.ValidationError(TG_PREVENT_CIRCULAR_CATEGORY)
            current = current.parent_category
        return value


class ProductSerializer(CustomModelSerializer):
    """
    MEH: Main Product full Information
    """
    title = serializers.CharField(required=True, min_length=3, max_length=78)
    type = CustomChoiceField(choices=ProductType.choices, default=ProductType.OFFSET)
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), required=False)
    category_display = serializers.StringRelatedField(source='category')
    template = serializers.PrimaryKeyRelatedField(queryset=TemplateFile.objects.all(), required=False)

    class Meta:
        model = Product
        fields = '__all__'
