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
    title = models.CharField(max_length=73, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    type = models.CharField(max_length=10, choices=ProductType.choices, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    category = models.ForeignKey("ProductCategory", on_delete=models.PROTECT, blank=False, null=False,
                                 related_name="category_product_list")
    # image = models.ImageField(upload_to="products/", blank=False, null=False)
    # icon = models.ImageField(upload_to="products/", blank=True, null=True)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    gallery = models.ForeignKey("GalleryCategory", on_delete=models.PROTECT, blank=True, null=True,
                                related_name="gallery_product_list")
    status = models.CharField(max_length=10, choices=ProductStatus.choices, default=ProductStatus.INACTIVE,
                              validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    private = models.BooleanField(default=False, blank=False, null=False)
    accounting_code = models.PositiveBigIntegerField(default=0, blank=False, null=False, verbose_name="Accounting Code")
    base_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Base Price")
    metadata = models.OneToOneField(Metadata, on_delete=models.PROTECT, blank=True, null=True,
                                    related_name="metadata_product")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f'TGP-{self.pk}: {self.title}'


class CountingUnit(models.TextChoices):
    NUMBER = "عدد"
    TIRAGE = "تیراژ"


class RoundPriceType(models.TextChoices):
    RN = "0"
    R10 = "10"
    R100 = "100"
    R1000 = "1000"


class ProductCategory(models.Model):
    title = models.CharField(max_length=73, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    parent_category = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, null=True, verbose_name="Parent Category",
                                        related_name="sub_categories")
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # video = models.FileField(upload_to="videos/", blank=False, null=False)
    # icon = models.ImageField(upload_to="ProductCategory/", blank=True, null=True)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    gallery = models.ForeignKey("GalleryCategory", on_delete=models.PROTECT, blank=True, null=True,
                                related_name="category_list")
    status = models.CharField(max_length=10, choices=ProductStatus.choices, default=ProductStatus.INACTIVE,
                              validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    accounting_code = models.PositiveBigIntegerField(default=0, blank=False, null=False, verbose_name="Accounting Code")
    fast_order = models.BooleanField(default=True, blank=False, null=False, verbose_name="Fast Order")
    fast_order_title = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                                        blank=True, null=True, verbose_name="Fast Order Title")
    counting_unit = models.CharField(max_length=10, choices=CountingUnit.choices, default=CountingUnit.NUMBER,
                                     blank=True, null=True, verbose_name="Counting Unit")
    free_order = models.BooleanField(default=True, blank=False, null=False, verbose_name="Free Order")
    round_price = models.CharField(max_length=4, choices=RoundPriceType.choices, default=RoundPriceType.RN,
                                   blank=False, null=False, verbose_name="Round Price")
    metadata = models.OneToOneField(Metadata, on_delete=models.PROTECT, blank=True, null=True,
                                    related_name="metadata_category")
    is_landing = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Landing")
    landing = models.OneToOneField(Landing, on_delete=models.PROTECT, blank=True, null=True,
                                   related_name="landing_category")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f'TGC-{self.pk}: {self.title}'


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
    title = models.CharField(max_length=10, choices=FieldName.choices, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    detail = models.JSONField(default=dict, blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    product = models.ForeignKey("Product", on_delete=models.PROTECT, blank=False, null=False,
                                related_name="product_fields")

    class Meta:
        ordering = ['-sort_number', 'product', 'product__category']
        verbose_name = "Product Field"
        verbose_name_plural = "Product Fields"

    def __str__(self):
        return f'Filed: {self.title} {self.product}'

    def size_method(self):
        sizeable = True
        self.detail = []

    def tirage_method(self):
        method = TirageMethod.FIX
        self.detail = []

    def copies_method(self):
        amount = 1
        self.detail = []

    def template_file_method(self):
        number = 1
        self.detail = []

    def design_method(self):
        self.detail = []

    def upload_file_method(self):
        # Gallery Choose of Upload File
        file_validation = True
        file_color_mode = FileColorMode.BOTH
        file_resolution = 300
        self.detail = []

    def color_inventory_method(self):
        self.detail = []


class GalleryImage(models.Model):
    title = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    # image_file = models.ImageField(upload_to="gallery/", blank=False, null=False)
    # image_thumbnail = models.ImageField(upload_to="gallery/", blank=False, null=False)
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    category = models.ForeignKey("GalleryCategory", on_delete=models.PROTECT, blank=True, null=True,
                                 related_name="category_images")

    class Meta:
        ordering = ['-sort_number', 'category']
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return f'Image {self.pk}: {self.title}'


class GalleryCategory(models.Model):
    title = models.CharField(max_length=73, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)

    # gallery_image_file = models.ImageField(upload_to="gallery/", blank=False, null=False)
    # gallery_image_thumbnail = models.ImageField(upload_to="gallery/", blank=False, null=False)
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    category = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, null=True,
                                 related_name="sub_galleries")

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"

    def __str__(self):
        return f'Gallery Category {self.pk}: {self.title}'


class Size(models.Model):
    name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(2)],
                            blank=False, null=False)
    display_name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(2)],
                            blank=False, null=False, verbose_name="Display Name")
    description = models.TextField(max_length=73, blank=True, null=True)
    length = models.FloatField(default=0, blank=False, null=False)
    width = models.FloatField(default=0, blank=False, null=False)
    base_cutting_edge = models.FloatField(default=0, blank=False, null=False, verbose_name="Base Cutting Edge")
    # size_icon = models.ImageField(upload_to="size_icon", blank=False, null=False)

    class Meta:
        ordering = ['display_name']
        verbose_name = "Size"
        verbose_name_plural = "Sizes"

    def __str__(self):
        return f'{self.display_name}'


class Tirage(models.Model):
    amount = models.PositiveSmallIntegerField(default=1, unique=True, blank=False, null=False)

    class Meta:
        ordering = ['amount']
        verbose_name = "Tirage"
        verbose_name_plural = "Tirages"

    def __str__(self):
        return f'Tirage {self.amount}'


class TemplateFile(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                                     blank=False, null=False, verbose_name="Template Name")
    description = models.TextField(max_length=73, blank=True, null=True)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    file_format = models.ForeignKey("FileType", on_delete=models.PROTECT, blank=False, null=False, verbose_name="File Format")
    # file = models.FileField(upload_to="files", blank=False, null=False)
    # image = models.ImageField(upload_to="images/", blank=False, null=False)

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Template File"
        verbose_name_plural = "Template Files"

    def __str__(self):
        return f'Template: {self.title}'


class Design(models.Model):
    title = models.CharField(max_length=37, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=100, blank=True, null=True)
    base_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Base Price')
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name='Sort Number')
    avg_duration = models.PositiveSmallIntegerField(default=0, blank=False, null=False, verbose_name='Average Duration')
    category = models.ForeignKey("ProductCategory", on_delete=models.PROTECT, blank=False, null=False,
                                 related_name="category_designs")

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Design"
        verbose_name_plural = "Designs"

    def __str__(self):
        return f'Design {self.pk}: {self.title}'


class FileType(models.Model):
    file_format = models.CharField(max_length=4, unique=True, validators=[validators.MinLengthValidator(2)],
                                   blank=False, null=False, verbose_name="File Format")
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    # file_icon = models.ImageField(upload_to='files', blank=False, null=False)

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "File Type"
        verbose_name_plural = "File Types"

    def __str__(self):
        return f'File Type {self.file_format}'


class Color(models.Model):
    name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    code = models.CharField(max_length=6, default="000", unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Color"
        verbose_name_plural = "Colors"

    def __str__(self):
        return f'Color {self.name}'


class OptionInputType(models.TextChoices):
    CHECKBOX = "چک باکس"
    RADIOBUTTON = "رادیو"
    WATERFALL = "آبشاری"
    TEXTFIELD = "متن"
    TEXTBOX = "ناحیه متنی"
    DATE = "تاریخ"
    FILE = "فایل"


class Option(models.Model):
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)],
                                    blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")
    base_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Base Price')
    is_numberize = models.BooleanField(default=False, blank=False, null=False, verbose_name="Is Numberize")
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Option"
        verbose_name_plural = "Options"

    def __str__(self):
        return f'Option: {self.title}'


class OptionCategory(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    input_type = models.CharField(max_length=10, choices=OptionInputType.choices, validators=[validators.MinLengthValidator(3)],
                                     blank=False, null=False, verbose_name="Input Type")
    # icon = models.ImageField(upload_to="services", blank=False, null=False)
    mandatory = models.BooleanField(default=False, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")
    hidden_price = models.BooleanField(default=False, blank=False, null=False, verbose_name="Hidden Price")
    after_print = models.BooleanField(default=False, blank=False, null=False, verbose_name="After Print")
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Option Category"
        verbose_name_plural = "Option Categories"

    def __str__(self):
        return f'Option Category: {self.title}'
