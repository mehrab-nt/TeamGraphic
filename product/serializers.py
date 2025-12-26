from rest_framework import serializers
from django.core.validators import RegexValidator
from file_manager.models import FileItem
from landing.models import Landing
from .models import Product, OffsetProduct, LargeFormatProduct, SolidProduct, DigitalProduct, ProductCategory, \
    ProductStatus, CountingUnit, RoundPriceType, GalleryCategory, GalleryImage, ProductFileField, Design, \
    Size, Duration, SheetPaper, Paper, Banner, Color, Folding, OptionCategory, Option, ProductOption, \
    PriceListCategory, PriceListTable
from api.responses import *
from api.mixins import CustomModelSerializer, CustomChoiceField
import json


class ProductCategoryListSerializer(CustomModelSerializer):
    """
    MEH: Product Category Brief Information for drop down list
    """
    class Meta:
        model = ProductCategory
        fields = ['id', 'title']


class ProductCategoryBriefSerializer(CustomModelSerializer):
    """
    MEH: Product Category Brief Information for product_explorer
    """
    type = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'title', 'status', 'status_display', 'sort_number', 'type', 'has_children']

    @staticmethod
    def get_type(obj):
        return 'dir'

    @staticmethod
    def get_has_children(obj):
        return obj.sub_categories.exists()

    @staticmethod
    def get_status_display(obj):
        return obj.get_status_display()


class ProductBriefSerializer(CustomModelSerializer):
    """
    MEH: Product Brief Information for product_explorer
    """
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'status', 'status_display', 'sort_number', 'type']

    @staticmethod
    def get_status_display(obj):
        return obj.get_status_display()


class ProductCategorySerializer(CustomModelSerializer):
    """
    MEH: Main Product Category full Information
    """
    title = serializers.CharField(required=True, min_length=3, max_length=78)
    description = serializers.CharField(default=None, allow_null=True, style={'base_template': 'textarea.html'})
    product_description = serializers.CharField(default=None, allow_null=True, style={'base_template': 'textarea.html'})
    parent_category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), required=False, allow_null=True)
    parent_category_display = serializers.StringRelatedField(source='parent_category')
    image = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='webp', seo_base=True), required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    icon = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='svg'), required=False, allow_null=True)
    icon_url = serializers.SerializerMethodField()
    video = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='mkv'), required=False, allow_null=True)
    video_url = serializers.SerializerMethodField()
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

    def update(self, instance, validated_data):
        if instance.status != validated_data['status']:
            instance = super().update(instance, validated_data)
            instance.update_all_subcategories_and_items() # MEH: Change all sub cat & pro Status
            return instance
        else:
            return super().update(instance, validated_data)


class ProductCategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    parent_path = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'title', 'parent_category', 'parent_path', 'has_children', 'children'
        ]

    @staticmethod
    def get_children(obj):
        children = obj.get_children()
        return ProductCategoryTreeSerializer(children, many=True).data

    @staticmethod
    def get_has_children(obj):
        return obj.get_children().exists()

    @staticmethod
    def get_parent_path(obj):
        return obj.get_slug_path()


class ProductInfoSerializer(CustomModelSerializer):
    """
    MEH: Product base Information
    Page 1 of Product Create & Edit (same for all)
    """
    title = serializers.CharField(required=True, min_length=3, max_length=78)
    parent_category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), required=False, allow_null=True)
    parent_category_display = serializers.StringRelatedField(source='parent_category')
    template = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.filter(type__in=['zip', 'rar', 'pdf', 'psd', 'cdr', 'jpg', 'jpeg']), required=False, allow_null=True)
    template_url = serializers.SerializerMethodField()
    image = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.filter(type='webp', seo_base=True), required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'sort_number', 'type', 'parent_category', 'parent_category_display', 'category_description',
                  'template', 'template_url', 'image', 'image_url', 'alt', 'status', 'status_lock', 'is_private', 'accounting_id', 'accept_copies', 'min_copies',
                  'total_order', 'last_order', 'total_main_sale', 'total_option_sale']
        read_only_fields = ['total_order', 'last_order', 'total_main_sale', 'total_option_sale']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and obj.image.file:
            url = obj.image.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_template_url(self, obj):
        request = self.context.get('request')
        if obj.template and obj.template.file:
            url = obj.template.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_fields(self): # MEH: for drop type in Update action (just in first Create)
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH']: # MEH: When Create, type assign and don't allow to change!
            fields.pop('type', None)
        return fields

    def create(self, validated_data):
        product = super().create(validated_data)
        if product.type == 'OFF': # MEH: Offset Product
            OffsetProduct.objects.create(product_info=product)
        elif product.type == 'LAR': # MEH: LargeFormat Product
            LargeFormatProduct.objects.create(product_info=product)
        elif product.type == 'SLD': # MEH: Solid Product
            SolidProduct.objects.create(product_info=product)
        elif product.type == 'DIG': # MEH: Digital Product
            DigitalProduct.objects.create(product_info=product)
        return product


class OffsetProductSerializer(CustomModelSerializer):
    """
    MEH: Page 2 of Product Edit (if Offset)
    """
    size_method_display = serializers.SerializerMethodField()
    size_list_display = serializers.SerializerMethodField()
    lat_size_display = serializers.StringRelatedField(source='lat_size', many=False, read_only=True)
    duration_list_display = serializers.SerializerMethodField()
    folding_list_display = serializers.SerializerMethodField()

    class Meta:
        model = OffsetProduct
        exclude = ['manual_price']
        read_only_fields = ['product_info']

    @staticmethod
    def get_size_method_display(obj):
        return obj.get_size_method_display()

    @staticmethod
    def get_size_list_display(obj):
        return [{'id': size.id, 'title': size.display_name} for size in obj.size_list.all()]

    @staticmethod
    def get_duration_list_display(obj):
        return [{'id': duration.id, 'title': duration.title} for duration in obj.duration_list.all()]

    @staticmethod
    def get_folding_list_display(obj):
        return [{'id': folding.id, 'title': folding.title} for folding in obj.folding_list.all()]


class LargeFormatProductSerializer(CustomModelSerializer):
    """
    MEH: Page 2 of Product Edit (if LargeFormat)
    """
    banner_list_display = serializers.StringRelatedField(source='banner_list', many=True, read_only=True)

    class Meta:
        model = LargeFormatProduct
        fields = '__all__'
        read_only_fields = ['product_info']


class SolidProductSerializer(CustomModelSerializer):
    """
    MEH: Page 2 of Product Edit (if Solid-Product)
    """
    color_inventory_list_display = serializers.StringRelatedField(source='color_inventory_list', many=True, read_only=True)

    class Meta:
        model = SolidProduct
        fields = '__all__'
        read_only_fields = ['product_info']


class DigitalProductSerializer(CustomModelSerializer):
    """
    MEH: Page 2 of Product Edit (if Digital)
    """
    size_method_display = serializers.SerializerMethodField()
    size_list_display = serializers.StringRelatedField(source='size_list', many=True, read_only=True)
    paper_list_display = serializers.StringRelatedField(source='paper_list', many=True, read_only=True)
    cover_paper_list_display = serializers.StringRelatedField(source='cover_paper_list', many=True, read_only=True)
    folding_list_display = serializers.StringRelatedField(source='folding_list', many=True, read_only=True)

    class Meta:
        model = DigitalProduct
        exclude = ['formula']
        read_only_fields = ['product_info']

    @staticmethod
    def get_size_method_display(obj):
        return obj.get_size_method_display()


class ProductGallerySerializer(CustomModelSerializer):
    """
    MEH: Page 3 of Product Edit (Gallery) same for all
    """
    gallery = serializers.PrimaryKeyRelatedField(queryset=GalleryCategory.objects.all(),
                                                 required=False, allow_null=True)
    gallery_type_display = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'gallery', 'gallery_type', 'gallery_type_display', 'gallery_multiple',]

    @staticmethod
    def get_gallery_type_display(obj):
        return obj.get_gallery_type_display()


class DesignDropDownSerializer(CustomModelSerializer):
    """
    MEH: Design id & title for drop-down list
    """
    class Meta:
        model = Design
        fields = ['id', 'title']


class DesignBriefSerializer(CustomModelSerializer):
    """
    MEH: Design brief Information
    """
    class Meta:
        model = Design
        fields = ['id', 'title', 'base_price', 'second_price', 'sort_number']


class DesignSerializer(CustomModelSerializer):
    """
    MEH: Design full Information
    """
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), required=True, many=True)
    category_display = serializers.StringRelatedField(source='category', many=True, read_only=True)
    image = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='webp', seo_base=True), required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    variant_type_display = serializers.SerializerMethodField()

    class Meta:
        model = Design
        fields = '__all__'
        read_only_fields = ['id', 'total_order', 'last_order', 'total_sale', 'category_display', 'image_url', 'variant_type_display']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and obj.image.file:
            url = obj.image.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    @staticmethod
    def get_variant_type_display(obj):
        return obj.get_variant_type_display()


class ProductDesignSerializer(CustomModelSerializer):
    """
    MEH: Page 4 of Product Edit (Designs) same for all
    """
    designs = serializers.PrimaryKeyRelatedField(queryset=Design.objects.all(), many=True, write_only=True,
                                                 required=False, allow_empty=True)
    designs_info = DesignSerializer(many=True, source='designs', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'designs', 'designs_info']


class FileFieldDropDownSerializer(CustomModelSerializer):
    """
    MEH: Design id & title for drop-down list
    """
    class Meta:
        model = ProductFileField
        fields = ['id', 'title']


class FileFieldBriefSerializer(CustomModelSerializer):
    """
    MEH: Design brief Information
    """
    class Meta:
        model = ProductFileField
        fields = ['id', 'title', 'sort_number']


class FileFieldSerializer(CustomModelSerializer):
    """
    MEH: File Field full Information
    """
    depend_on = serializers.PrimaryKeyRelatedField(queryset=ProductFileField.objects.all(), required=False, allow_null=True)
    depend_on_display = serializers.StringRelatedField(source='depend_on', read_only=True)

    class Meta:
        model = ProductFileField
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance and isinstance(instance, ProductFileField):
            self.fields['depend_on'].queryset = ProductFileField.objects.exclude(pk=instance.pk)


class ProductFileSerializer(CustomModelSerializer):
    """
    MEH: Page 5 of Product Edit (Files)
    """
    files = serializers.PrimaryKeyRelatedField(queryset=ProductFileField.objects.all(), many=True, write_only=True,
                                               required=False, allow_empty=True)
    files_info = FileFieldSerializer(many=True, source='files', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'check_file', 'show_cutting_edge', 'files', 'files_info']


class ProductOptionSerializer(CustomModelSerializer):
    """
    MEH: Page 6 of Product Edit (Options)
    """
    dependent_option = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = ProductOption
        exclude = ['id', 'product']


class ProductManualPriceSerializer(OffsetProductSerializer):
    """
    MEH: Page 7 of Product Edit (manual Price) if Offset
    """
    manual_price = serializers.JSONField(required=True)

    class Meta:
        model = OffsetProduct
        fields = '__all__'
        extra_kwargs = {
            field.name: {'read_only': True}
            for field in model._meta.get_fields()
            if field.name != 'manual_price'
        }

    @staticmethod
    def validate_manual_price(value):
        if len(json.dumps(value)) > 1999:
            raise serializers.ValidationError("field_list JSON is too large.")
        if not isinstance(value, dict):
            raise serializers.ValidationError("field_list must be a dictionary.")
        # required_keys = {"item_list"}
        # if not required_keys.issubset(value):
        #     raise serializers.ValidationError("field_list must include 'item_list' keys.")
        # items = value.get('item_list')
        # if not isinstance(items, list) or not items:
        #     raise serializers.ValidationError("item_list must be a non-empty list.")
        # for item in items:
        #     if not isinstance(item, dict):
        #         raise serializers.ValidationError("Each item in item_list must be a dictionary.")
        #     if 'key' not in item or 'value' not in item:
        #         raise serializers.ValidationError("Each item must contain 'key' and 'value'")
        #     if not isinstance(item['key'], str) or len(item['key']) > 10:
        #         raise serializers.ValidationError("Each key must be a string with max 10 characters.")
        #     if not isinstance(item['value'], (int, float)):
        #         raise serializers.ValidationError("Each value must be a number.")
        # return value


class ProductFormulaPriceSerializer(DigitalProductSerializer):
    """
    MEH: Page 7 of Product Edit (formula Price) if Digital
    """
    formula = serializers.CharField(style={'base_template': 'textarea.html'}, required=True)

    class Meta:
        model = DigitalProduct
        fields = '__all__'
        extra_kwargs = {
            field.name: {'read_only': True}
            for field in model._meta.get_fields()
            if field.name != 'formula'
        }


class SizeSerializer(CustomModelSerializer):
    """
    MEH: Main Product Field (Size) full Information
    """
    class Meta:
        model = Size
        fields = '__all__'


class DurationSerializer(CustomModelSerializer):
    """
    MEH: Main Product Field (Duration) full Information
    """
    class Meta:
        model = Duration
        fields = '__all__'


class BannerSerializer(CustomModelSerializer):
    """
    MEH: Main Product Field (Banner) full Information
    """
    class Meta:
        model = Banner
        exclude = ['total_print', 'total_gap', 'total_leaf', 'total_waste']


class ColorSerializer(CustomModelSerializer):
    """
    MEH: Main Product Field (Color) full Information
    """
    class Meta:
        model = Color
        fields = '__all__'


class SheetPaperSerializer(CustomModelSerializer):
    """
    MEH: Main Product Field (Sheet-Paper) full Information
    """
    class Meta:
        model = SheetPaper
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action == 'list':  # MEH: brief view for list
            for field in ['material', 'description', 'weight', 'cutting_price']:
                data.pop(field, None)
        return data


class PaperSerializer(CustomModelSerializer):
    """
    MEH: Main Product Field (Paper) full Information
    """
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all())
    size_display = serializers.StringRelatedField(source='size', read_only=True)
    sheet_paper = serializers.PrimaryKeyRelatedField(queryset=SheetPaper.objects.all())
    sheet_paper_display = serializers.StringRelatedField(source='sheet_paper', read_only=True)

    class Meta:
        model = Paper
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action == 'list': # MEH: brief view for list
            for field in ['color_print_price', 'baw_print_price', 'cutting_price', 'folding_price']:
                data.pop(field, None)
        return data


class FoldingSerializer(CustomModelSerializer):
    """
    MEH: Main Product Folding (Paper) full Information
    """
    class Meta:
        model = Folding
        fields = '__all__'


class GalleryDropDownSerializer(CustomModelSerializer):
    """
    MEH: Gallery Category id & name for drop-down list
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = GalleryCategory
        fields = ["id", "name"]

    @staticmethod
    def get_name(obj):
        prefix = "-" * obj.level if obj.level > 0 else ""
        return f"{prefix}{obj.name}"


class GalleryCategoryBriefSerializer(CustomModelSerializer):
    """
    MEH: Gallery Category Brief Information for gallery_explorer
    """
    type = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()

    class Meta:
        model = GalleryCategory
        fields = ['id', 'name', 'sort_number', 'type', 'has_children', 'parent_category']

    @staticmethod
    def get_type(obj):
        return 'dir'

    @staticmethod
    def get_has_children(obj):
        return obj.sub_galleries.exists()

    @staticmethod
    def get_parent_category(obj):
        if obj.parent_category:
            return obj.parent_category.name
        else:
            return None


class GalleryImageBriefSerializer(CustomModelSerializer):
    """
    MEH: Gallery Image Brief Information for gallery_explorer
    """
    type = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ['id', 'name', 'sort_number', 'type', 'preview', 'image_file', 'parent_category', 'alt']

    @staticmethod
    def get_type(obj):
        return 'img'

    @staticmethod
    def get_parent_category(obj):
        if obj.parent_category:
            return obj.parent_category.name
        else:
            return None


class GalleryCategoryTreeSerializer(CustomModelSerializer):
    children = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    parent_path = serializers.SerializerMethodField()

    class Meta:
        model = GalleryCategory
        fields = [
            'id', 'name', 'parent_category', 'parent_path', 'has_children', 'children'
        ]

    @staticmethod
    def get_children(obj):
        children = obj.get_children()
        return GalleryCategoryTreeSerializer(children, many=True).data

    @staticmethod
    def get_has_children(obj):
        return obj.get_children().exists()

    @staticmethod
    def get_parent_path(obj):
        return obj.get_slug_path()


class GalleryCategorySerializer(CustomModelSerializer):
    """
    MEH: Gallery Category Full Information for gallery_explorer
    """
    type = serializers.SerializerMethodField()
    parent_category = serializers.PrimaryKeyRelatedField(queryset=GalleryCategory.objects.all(), required=False, allow_null=True)

    class Meta:
        model = GalleryCategory
        fields = '__all__'

    @staticmethod
    def get_type(obj):
        return 'dir'

    def get_fields(self): # MEH: for drop parent_category in Update action (just in first Create)
        fields = super().get_fields()
        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH']: # MEH: When Create, parent_category assign and don't allow to change!
            fields.pop('parent_category', None)
        return fields


class GalleryImageSerializer(CustomModelSerializer):
    """
    MEH: Gallery Item Full Information for gallery_explorer
    (img width & height can set manually for final optimized image size)
    """
    name = serializers.CharField(required=False, allow_null=True, min_length=3, max_length=78)
    preview = serializers.ImageField(read_only=True)
    type = serializers.CharField(read_only=True)
    img_width = serializers.IntegerField(default=0, write_only=True, required=False)
    img_height = serializers.IntegerField(default=0, write_only=True, required=False)
    parent_category = serializers.PrimaryKeyRelatedField(queryset=GalleryCategory.objects.all(), required=False, allow_null=True)

    class Meta:
        model = GalleryImage
        fields = '__all__'

    def validate(self, data): # MEH: Check uploaded Image size and Image -> Always SEO Base request (Optimize in filemanager.images.py)
        file = data.get('image_file')
        width = data.pop('img_width', 0)
        height = data.pop('img_height', 0)
        if file:
            size_mb = file.size / (1024 * 1024)
            if size_mb > 10:
                raise serializers.ValidationError(TG_MAX_FILE_SIZE + str(size_mb) + 'MB')
            data['image_file'] = self.validate_upload_image(file, max_image_size=10, max_width=None, max_height=None, size=(width, height)) # MEH: Change image to SEO base friendly format
        return data

    # def get_fields(self): # MEH: for drop image in Update action (just in first Create)
    #     fields = super().get_fields()
    #     request = self.context.get('request')
    #     if request and request.method in ['PUT', 'PATCH']: # MEH: When Create, image assign and don't allow to change!
    #         fields.pop('image_file', None)
    #     return fields


class OptionCategoryBriefSerializer(CustomModelSerializer):
    """
    MEH: Option Category Brief Information for option_explorer
    """
    type = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()

    class Meta:
        model = OptionCategory
        fields = ['id', 'title', 'is_active', 'sort_number', 'type', 'icon', 'has_children', 'parent_category']

    @staticmethod
    def get_type(obj):
        return 'dir'

    @staticmethod
    def get_has_children(obj):
        return obj.sub_categories.exists()

    @staticmethod
    def get_parent_category(obj):
        if obj.parent_category:
            return obj.parent_category.title
        else:
            return None


class OptionBriefSerializer(CustomModelSerializer):
    """
    MEH: Option Information for option_explorer
    """
    type = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ['id', 'title', 'base_amount', 'is_active', 'sort_number', 'type']

    @staticmethod
    def get_type(obj):
        return 'opt'


class OptionCategorySerializer(CustomModelSerializer):
    """
    MEH: Option Category Full Information
    """
    parent_category = serializers.PrimaryKeyRelatedField(queryset=OptionCategory.objects.all(), required=False, allow_null=True)
    icon = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all(), required=False, allow_null=True)
    icon_url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    input_type_display = serializers.SerializerMethodField()

    class Meta:
        model = OptionCategory
        fields = '__all__'

    @staticmethod
    def get_type(obj):
        return 'dir'

    def get_icon_url(self, obj):
        request = self.context.get('request')
        if obj.icon and obj.icon.file:
            url = obj.icon.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    @staticmethod
    def get_input_type_display(obj):
        return obj.get_input_type_display()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance and isinstance(instance, OptionCategory):
            self.fields['parent_category'].queryset = OptionCategory.objects.exclude(pk=instance.pk)

    def update(self, instance, validated_data):
        if instance.is_active != validated_data['is_active']:
            instance = super().update(instance, validated_data)
            instance.update_all_subcategories_and_items() # MEH: Change all sub cat & opt is_active
            return instance
        else:
            return super().update(instance, validated_data)


class OptionSerializer(CustomModelSerializer):
    """
    MEH: Option Full Information
    """
    class Meta:
        model = Option
        fields = '__all__'


class OptionSelectListSerializer(CustomModelSerializer):
    """
    MEH: Option Full list for select
    for Page 6 of Product Edit (Options)
    """
    class Meta:
        model = Option
        fields = ['id', 'title', 'is_numberize', 'base_amount', 'price_type']


class OptionCategoryTreeSerializer(CustomModelSerializer):
    children = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    parent_path = serializers.SerializerMethodField()

    class Meta:
        model = OptionCategory
        fields = ['id', 'title', 'children', 'parent_path', 'has_children', 'parent_category']

    @staticmethod
    def get_children(obj):
        children = obj.get_children()
        return OptionCategoryTreeSerializer(children, many=True).data

    @staticmethod
    def get_has_children(obj):
        return obj.get_children().exists()

    @staticmethod
    def get_parent_path(obj):
        return obj.get_slug_path()


class OptionCategorySelectListSerializer(CustomModelSerializer):
    children = serializers.SerializerMethodField()
    option_list = serializers.SerializerMethodField()

    class Meta:
        model = OptionCategory
        fields = ['id', 'title', 'children', 'option_list']

    @staticmethod
    def get_children(obj):
        children = obj.get_children()
        if children.exists():
            return OptionCategorySelectListSerializer(children, many=True).data
        return []

    @staticmethod
    def get_option_list(obj):
        options = obj.option_list.filter(is_active=True)
        return OptionSelectListSerializer(options, many=True).data


class OptionProductListSerializer(CustomModelSerializer):
    """
    MEH: Option Full list of related Product
    """
    product_display = serializers.StringRelatedField(source='product')
    product_category = serializers.SerializerMethodField()

    class Meta:
        model = ProductOption
        fields = ['product', 'product_display', 'product_category']

    @staticmethod
    def get_product_category(obj):
        return str(obj.product.get_category_path())


class ProductInCategorySerializer(CustomModelSerializer):
    """
    MEH: for Table of product in category (with fields)
    """
    parent_path = serializers.SerializerMethodField()
    parent_category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'parent_path', 'parent_category', 'type']

    @staticmethod
    def get_parent_path(obj):
        return obj.get_category_path()


class PriceListCategoryBriefSerializer(CustomModelSerializer):
    """
    MEH: Price List Category Brief Information for price_list_explorer
    """
    type = serializers.SerializerMethodField()

    class Meta:
        model = PriceListCategory
        fields = ['id', 'title', 'is_active', 'sort_number', 'type']

    @staticmethod
    def get_type(obj):
        return 'dir'


class PriceListTableBriefSerializer(CustomModelSerializer):
    """
    MEH: Price List Table Brief Information for price_list_explorer
    """
    class Meta:
        model = PriceListTable
        fields = ['id', 'title', 'is_active', 'sort_number', 'type']


class PriceListCategorySerializer(CustomModelSerializer):
    """
    MEH: Price List Category Full Information
    """
    parent_category = serializers.PrimaryKeyRelatedField(queryset=PriceListCategory.objects.all(), required=False, allow_null=True)
    image = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='webp', seo_base=True), required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PriceListCategory
        fields = '__all__'

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and obj.image.file:
            url = obj.image.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance and isinstance(instance, PriceListCategory):
            self.fields['parent_category'].queryset = PriceListCategory.objects.exclude(pk=instance.pk)

    def update(self, instance, validated_data):
        if instance.is_active != validated_data['is_active']:
            instance = super().update(instance, validated_data)
            instance.update_all_subcategories_and_items() # MEH: Change all sub cat & table is_active
            return instance
        else:
            return super().update(instance, validated_data)


class PriceListTableSerializer(CustomModelSerializer):
    """
    MEH: Price List Table Full Information
    """
    image = serializers.PrimaryKeyRelatedField(queryset=FileItem.objects.all().filter(type='webp', seo_base=True), required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    price_list_categories = serializers.PrimaryKeyRelatedField(queryset=PriceListCategory.objects.all(), required=False, allow_null=True, many=True)
    price_list_categories_display = serializers.StringRelatedField(source='price_list_categories', many=True, read_only=True)
    product_category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), required=True, allow_null=False)
    product_category_display = serializers.StringRelatedField(source='product_category', read_only=True)
    product_list = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = PriceListTable
        fields = '__all__'

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and obj.image.file:
            url = obj.image.file.url
            return request.build_absolute_uri(url) if request else url
        return None
