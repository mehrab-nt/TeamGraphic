from rest_framework import serializers
from django.core.validators import RegexValidator

from landing.models import Landing
from .models import Product, ProductType, ProductCategory, GalleryCategory, ProductStatus, TemplateFile, CountingUnit, \
    RoundPriceType
from api.responses import *
from api.mixins import CustomModelSerializer, CustomChoiceField
from config.images import *


class ProductCategoryBriefSerializer(CustomModelSerializer):
    """
    MEH: Product Category Brief Information for product_explorer
    """
    list_type = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'title', 'status', 'sort_number', 'list_type', 'has_children']

    @staticmethod
    def get_list_type(obj):
        return 'category'

    @staticmethod
    def get_has_children(obj):
        return obj.sub_categories.exists()


class ProductBriefSerializer(CustomModelSerializer):
    """
    MEH: Product Brief Information for product_explorer
    """
    list_type = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'status', 'sort_number', 'list_type']

    @staticmethod
    def get_list_type(obj):
        return 'product'


class ProductCategorySerializer(CustomModelSerializer):
    """
    MEH: Main Product Category full Information
    """
    title = serializers.CharField(required=True, min_length=3, max_length=78)
    description = serializers.CharField(default=None, allow_null=True, style={'base_template': 'textarea.html'})
    parent_category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), required=False, allow_null=True)
    parent_category_display = serializers.StringRelatedField(source='parent_category')
    image = serializers.ImageField(required=False, allow_null=True)
    icon = serializers.ImageField(required=False, allow_null=True)
    gallery = serializers.PrimaryKeyRelatedField(queryset=GalleryCategory.objects.all(), required=False)
    status = CustomChoiceField(choices=ProductStatus.choices, initial=ProductStatus.ACTIVE, default=ProductStatus.ACTIVE)
    accounting_id = serializers.IntegerField(default=None,
                                             validators=[RegexValidator(regex=r'^\d{1,16}$', message=TG_DATA_WRONG)])
    counting_unit = CustomChoiceField(choices=CountingUnit.choices, initial=CountingUnit.TIRAGE, default=CountingUnit.TIRAGE)
    round_price = CustomChoiceField(choices=RoundPriceType.choices, initial=RoundPriceType.DEF, default=RoundPriceType.DEF)
    landing = serializers.PrimaryKeyRelatedField(queryset=Landing.objects.all(), required=False)

    class Meta:
        model = ProductCategory
        fields = '__all__'

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

# class ProductSerializer(CustomModelSerializer):
#     """
#     MEH: Main Product full Information
#     """
#     title = serializers.CharField(required=True, min_length=3, max_length=78)
#     type = CustomChoiceField(choices=ProductType.choices, default=ProductType.OFFSET)
#     category = serializers.PrimaryKeyRelatedField(required=True, )
#     category_display = serializers.StringRelatedField(source='category')
#     template = serializers.PrimaryKeyRelatedField(queryset=TemplateFile.objects.all(), required=False)
#
#     class Meta:
#         model = Product
#         fields = '__all__'
