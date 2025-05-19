from django.db import models
from django.core import validators
from pages.models import Metadata, Landing


class ProductType(models.TextChoices):
    OFFSET = "افست"
    LARGE_FORMAT = "لارج فرمت"
    DIGITAL = "دیجیتال"
    ITEM = "محصول"
    OTHER = "سایر"


class ProductStatus(models.TextChoices):
    ACTIVE = "فعال"
    INACTIVE = "غیر فعال"
    UPDATING = "بروزرسانی"


class Product(models.Model):
    product_name = models.CharField(max_length=73, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    product_type = models.CharField(max_length=10, choices=ProductType.choices, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    category = models.ForeignKey("ProductCategory", on_delete=models.PROTECT, related_name="products",
                                 blank=False, null=False)
    # image = models.ImageField(upload_to="products/", blank=False, null=False)
    # icon = models.ImageField(upload_to="products/", blank=True, null=True)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
    gallery = models.ForeignKey("GalleryCategory", on_delete=models.PROTECT, related_name="product_list",
                                blank=True, null=True)
    status = models.CharField(max_length=10, choices=ProductStatus.choices, default=ProductStatus.INACTIVE,
                              validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    private = models.BooleanField(default=False, blank=False, null=False)
    accounting_code = models.IntegerField(default=0, blank=False, null=False)
    base_price = models.IntegerField(default=0, blank=False, null=False)
    metadata = models.OneToOneField(Metadata, on_delete=models.PROTECT, related_name="metadata_product",
                                    blank=True, null=True)


class CountingUnit(models.TextChoices):
    NUMBER = "عدد"
    TIRAGE = "تیراژ"


class RoundPriceType(models.TextChoices):
    RN = "0"
    R10 = "10"
    R100 = "100"
    R1000 = "1000"


class ProductCategory(models.Model):
    category_name = models.CharField(max_length=73, unique=True, validators=[validators.MinLengthValidator(3)],
                                     blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    parent_category = models.ForeignKey("self", on_delete=models.PROTECT, related_name="sub_categories",
                                        blank=True, null=True)
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # video = models.FileField(upload_to="videos/", blank=False, null=False)
    # icon = models.ImageField(upload_to="ProductCategory/", blank=True, null=True)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
    gallery = models.ForeignKey("GalleryCategory", on_delete=models.PROTECT, related_name="category_list",
                                blank=True, null=True)
    status = models.CharField(max_length=10, choices=ProductStatus.choices, default=ProductStatus.INACTIVE,
                              validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    accounting_code = models.IntegerField(default=0, blank=False, null=False)
    short_order = models.BooleanField(default=True, blank=False, null=False)
    short_order_title = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                                         blank=True, null=True)
    counting_unit = models.CharField(max_length=10, choices=CountingUnit.choices, default=CountingUnit.NUMBER,
                                     blank=True, null=True)
    free_order = models.BooleanField(default=True, blank=False, null=False)
    round_price = models.CharField(max_length=4, choices=RoundPriceType.choices, default=RoundPriceType.RN,
                                   blank=False, null=False)
    metadata = models.OneToOneField(Metadata, on_delete=models.PROTECT, related_name="metadata_category",
                                    blank=True, null=True)
    is_landing = models.BooleanField(default=True, blank=False, null=False)
    landing = models.OneToOneField(Landing, on_delete=models.PROTECT, related_name="landing_category",
                                   blank=True, null=True)


class FieldName(models.TextChoices):
    SIZE = "سایز"
    TIRAGE = "تیراژ"
    COPIES = 'نسخه'
    TEMPLATE = 'قالب'
    UPLOAD_FILE = "فایل"
    COLOR = "رنگ"


class SizeMethod(models.TextChoices):
    FIX = "ثابت"
    VARIABLE = "متغیر"


class FileColorMode(models.TextChoices):
    CMYK = "CMYK"
    RGB = "RGB"
    BOTH = "هر دو"


class TirageMethod(models.TextChoices):
    FIX = "ثابت"
    OPTIONAL = "دلخواه"
    RATIO = "نسبت دار"


class ProductField(models.Model):
    field_name = models.CharField(max_length=10, choices=FieldName.choices, validators=[validators.MinLengthValidator(3)],
                                  blank=False, null=False)
    field_json = models.JSONField(default=dict, blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
    product = models.ForeignKey("Product", on_delete=models.PROTECT, related_name="fields",
                                blank=False, null=False)

    def size_method(self):
        sizeable = True
        self.field_json = []

    def tirage_method(self):
        method = TirageMethod.FIX
        self.field_json = []

    def copies_method(self):
        amount = 1
        self.field_json = []

    def template_file_method(self):
        number = 1
        self.field_json = []

    def design_method(self):
        self.field_json = []

    def upload_file_method(self):
        # Gallery Choose of Upload File
        file_validation = True
        file_color_mode = FileColorMode.BOTH
        file_resolution = 300
        self.field_json = []

    def color_inventory_method(self):
        self.field_json = []


class GalleryImage(models.Model):
    image_name = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                                  blank=False, null=False)
    image_alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                                 blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
    # image_file = models.ImageField(upload_to="gallery/", blank=False, null=False)
    # image_thumbnail = models.ImageField(upload_to="gallery/", blank=False, null=False)
    category = models.ForeignKey("GalleryCategory", on_delete=models.PROTECT, related_name="images",
                                 blank=True, null=True)


class GalleryCategory(models.Model):
    gallery_name = models.CharField(max_length=73, unique=True, validators=[validators.MinLengthValidator(3)],
                                    blank=False, null=False)
    gallery_alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                                   blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
    # gallery_image_file = models.ImageField(upload_to="gallery/", blank=False, null=False)
    # gallery_image_thumbnail = models.ImageField(upload_to="gallery/", blank=False, null=False)
    category = models.ForeignKey("self", on_delete=models.PROTECT, related_name="sub_galleries",
                                 blank=True, null=True)


class Size(models.Model):
    name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(2)],
                            blank=False, null=False)
    display_name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(2)],
                            blank=False, null=False)
    description = models.TextField(max_length=73, blank=True, null=True)
    length = models.IntegerField(default=0, blank=False, null=False)
    width = models.IntegerField(default=0, blank=False, null=False)
    base_cutting_edge = models.IntegerField(default=0, blank=False, null=False)
    # size_icon = models.ImageField(upload_to="size_icon", blank=False, null=False)


class Tirage(models.Model):
    amount = models.IntegerField(default=1, unique=True, validators=[validators.MinValueValidator(1),
                                                                     validators.MaxValueValidator(100000)],
                                 blank=False, null=False)


class TemplateFile(models.Model):
    template_name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                                     blank=False, null=False)
    description = models.TextField(max_length=73, blank=True, null=True)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
    file_format = models.ForeignKey("FileType", on_delete=models.PROTECT, blank=False, null=False)
    # file = models.FileField(upload_to="files", blank=False, null=False)
    # image = models.ImageField(upload_to="images/", blank=False, null=False)


class Design(models.Model):
    name = models.CharField(max_length=37, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    description = models.TextField(max_length=100, blank=True, null=True)
    base_price = models.IntegerField(default=0, blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
    avg_duration = models.IntegerField(default=0, blank=False, null=False)
    category = models.ForeignKey("ProductCategory", on_delete=models.PROTECT, related_name="designs",
                                 blank=False, null=False)


class FileType(models.Model):
    file_format_name = models.CharField(max_length=4, unique=True, validators=[validators.MinLengthValidator(2)],
                                   blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
    # file_icon = models.ImageField(upload_to='files', blank=False, null=False)


class Color(models.Model):
    color_name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                                  blank=False, null=False)
    color_code = models.CharField(max_length=6, default="000", unique=True, validators=[validators.MinLengthValidator(3)],
                                  blank=False, null=False)


class OptionInputType(models.TextChoices):
    CHECKBOX = "چک باکس"
    RADIOBUTTON = "رادیو"
    WATERFALL = "آبشاری"
    TEXTFIELD = "متن"
    TEXTBOX = "ناحیه متنی"
    DATE = "تاریخ"
    FILE = "فایل"


class Option(models.Model):
    service_name = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)],
                                    blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=False, null=False)
    base_price = models.IntegerField(default=0, blank=False, null=False)
    is_number = models.BooleanField(default=False, blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False)


class OptionCategory(models.Model):
    service_category_name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                                             blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    input_type = models.CharField(max_length=10, choices=OptionInputType.choices, validators=[validators.MinLengthValidator(3)],
                                     blank=False, null=False)
    # icon = models.ImageField(upload_to="services", blank=False, null=False)
    mandatory = models.BooleanField(default=False, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=False, null=False)
    hidden_price = models.BooleanField(default=False, blank=False, null=False)
    after_print = models.BooleanField(default=False, blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False)
