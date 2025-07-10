from django.db import models
from django.core import validators
from landing.models import Landing
from file_manager.models import FileItem
from file_manager.images import *
from django.core.exceptions import ValidationError
from api.responses import TG_PREVENT_CIRCULAR_CATEGORY


class ProductStatus(models.TextChoices):
    ACTIVE = 'AC', 'فعال'
    INACTIVE = 'IN', 'غیر فعال'
    UPDATING = 'UP', 'بروزرسانی'


class CountingUnit(models.TextChoices):
    NUMBER = 'NUM', 'عدد'
    TIRAGE = 'TIR', "تیراژ"


class RoundPriceType(models.IntegerChoices):
    BASE = 0
    R10 = 10
    R100 = 100
    R1000 = 1000
    DEF = -1


class ProductCategory(models.Model):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.PROTECT,
                                        blank=True, null=True, verbose_name='Parent Category',
                                        related_name='sub_categories')
    image = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='image_for_product_categories')
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=True, null=False)
    icon = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                             blank=True, null=True,
                             related_name='icon_for_product_categories')
    video = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='video_for_product_categories')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    gallery = models.ForeignKey('GalleryCategory', on_delete=models.PROTECT,
                                blank=True, null=True,
                                related_name='linked_product_category_list')
    status = models.CharField(max_length=2, validators=[validators.MinLengthValidator(2)],
                              choices=ProductStatus.choices, default=ProductStatus.ACTIVE,
                              blank=False, null=False)
    accounting_id = models.PositiveBigIntegerField(default=0,
                                                   blank=True, null=True, verbose_name='Accounting ID')
    fast_order = models.BooleanField(default=True,
                                     blank=False, null=False, verbose_name='Fast Order')
    fast_order_title = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                                        blank=True, null=True, verbose_name='Fast Order Title')
    counting_unit = models.CharField(max_length=3, validators=[validators.MinLengthValidator(2)],
                                     choices=CountingUnit.choices, default=CountingUnit.NUMBER,
                                     blank=True, null=True, verbose_name="Counting Unit")
    free_order = models.BooleanField(default=True, blank=False, null=False, verbose_name="Free Order")
    round_price = models.SmallIntegerField(choices=RoundPriceType.choices, default=RoundPriceType.DEF,
                                           blank=True, null=True, verbose_name='Round Price')
    is_landing = models.BooleanField(default=True,
                                     blank=False, null=False, verbose_name='Is Landing')
    landing = models.OneToOneField(Landing, on_delete=models.PROTECT,
                                   blank=True, null=True,
                                   related_name='landing_product_category')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['sort_number', 'title']

    def __str__(self):
        return f'TGC-{self.pk}: {self.title}'

    def save(self, *args, **kwargs):
        if self.image and not self.alt:
            self.alt = f'{self.title}عکس دسته محصولات '
        if self.fast_order and not self.fast_order_title:
            self.fast_order_title = self.title
        if self.landing:
            self.is_landing = True
        super().save(*args, **kwargs)

    def clean(self): # MEH: Prevent circular reference A → B → C → A in Admin Panel
        current = self.parent_category
        while current:
            if current == self:
                raise ValidationError(TG_PREVENT_CIRCULAR_CATEGORY)
            current = current.parent_category


class ProductType(models.TextChoices):
    OFFSET = 'OFF', 'افست'
    LARGE_FORMAT = 'LAR', 'لارج فرمت'
    DIGITAL = 'DIG', 'دیجیتال'
    ITEM = 'ITM', 'محصول عمومی'


class Product(models.Model):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=ProductType.choices,
                            blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    parent_category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='product_list')
    image = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='image_for_products')
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=True, null=False)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    template = models.ForeignKey('TemplateFile', on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name='product_list')
    gallery = models.ForeignKey('GalleryCategory', on_delete=models.PROTECT,
                                blank=True, null=True,
                                related_name='linked_product_list')
    status = models.CharField(max_length=2, validators=[validators.MinLengthValidator(2)],
                              choices=ProductStatus.choices, default=ProductStatus.ACTIVE,
                              blank=False, null=False)
    is_private = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='Is Private')
    accounting_id = models.PositiveBigIntegerField(default=0,
                                                   blank=True, null=True, verbose_name='Accounting ID')
    price = models.JSONField(default=dict,
                             blank=False, null=False)
    options = models.ManyToManyField(
        'Option',
        through='ProductOption',
        through_fields=('product', 'option')
    )
    inventory = models.SmallIntegerField(default=-1, blank=False, null=False)
    is_landing = models.BooleanField(default=True,
                                     blank=False, null=False, verbose_name='Is Landing')
    landing = models.OneToOneField(Landing, on_delete=models.PROTECT,
                                   blank=True, null=True,
                                   related_name='landing_product')
    total_order = models.PositiveIntegerField(default=0,
                                              blank=False, null=False, verbose_name='Total Order')
    last_order = models.DateField(blank=True, null=True, verbose_name='Last Order')
    total_main_sale = models.PositiveIntegerField(default=0,
                                                  blank=False, null=False, verbose_name='Total Main Sale')
    total_option_sale = models.PositiveIntegerField(default=0,
                                                    blank=False, null=False, verbose_name='Total Option Sale')

    class Meta:
        ordering = ('parent_category', '-sort_number')
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f'TGP-{self.pk}: {self.title}'

    def save(self, *args, **kwargs):
        if self.image and not self.alt:
            self.alt = f'{self.title}عکس محصول '
        super().save(*args, **kwargs)


class TemplateFile(models.Model):
    name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    description = models.TextField(max_length=78,
                                   blank=True, null=True)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    file = models.OneToOneField(FileItem, on_delete=models.SET_NULL,
                                blank=True, null=True, related_name='template_file')
    # image = models.ImageField(upload_to="images/", blank=False, null=False)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)
    download_counter = models.PositiveSmallIntegerField(default=0,
                                                      blank=False, null=False, verbose_name='Download Counter')

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Template File"
        verbose_name_plural = "Template Files"

    def __str__(self):
        return f'Template: {self.name}'


class GalleryCategory(models.Model):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    # gallery_image_file = models.ImageField(upload_to="gallery/", blank=False, null=False)
    # gallery_image_thumbnail = models.ImageField(upload_to="gallery/", blank=False, null=False)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    parent_category = models.ForeignKey('self', on_delete=models.PROTECT,
                                        blank=True, null=True,
                                        related_name='sub_galleries')
    active_link = models.BooleanField(default=False,
                                      blank=False, null=False, verbose_name='Active Link')

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Gallery Category'
        verbose_name_plural = 'Gallery Categories'

    def __str__(self):
        return f'Gallery Category #{self.pk}: {self.title}'


class GalleryImage(models.Model):
    title = models.CharField(max_length=78, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    # image_file = models.ImageField(upload_to="gallery/", blank=False, null=False)
    # image_thumbnail = models.ImageField(upload_to="gallery/", blank=False, null=False)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    category = models.ForeignKey(GalleryCategory, on_delete=models.PROTECT,
                                 blank=True, null=True,
                                 related_name='gallery_image_list')

    class Meta:
        ordering = ['-sort_number', 'category']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def __str__(self):
        return f'Image #{self.pk}: {self.title}'


class FieldName(models.TextChoices):
    FACE = 'FAC', 'وجه'
    SIZE = 'SIZ', 'ابعاد'
    PAPER_TYPE = 'PAP', 'جنس'
    TIRAGE = 'TIR', 'تیراژ'
    COPIES = 'COP', 'نسخه'
    DESIGN = 'DES', 'طراحی'
    UPLOAD_FILE = 'UPF', 'فایل'
    COLOR = 'COL', 'رنگ'
    DURATION = 'DUR', 'تحویل کاری'
    BANNER = 'BAN', 'مشخصات بنر'


class FaceType(models.TextChoices):
    ONE = 'ONE', 'یک رو'
    TWO = 'TOW', 'دو رو'


class SizeMethod(models.TextChoices):
    FIX = 'FIX', 'ثابت'
    OPTIONAL = 'OPT', 'دلخواه'


class TirageMethod(models.TextChoices):
    FIX = 'FIX', 'ثابت'
    OPTIONAL = 'OPT', 'دلخواه'


class FileColorMode(models.TextChoices):
    CMYK = 'CMYK', 'CMYK'
    RGB = 'RGB', 'RGB'
    BOTH = 'BOTH', 'هر دو'


class FieldPriceType(models.TextChoices):
    NONE = 'NON', 'ندارد'
    FORMULA = 'FOR', 'فرمول'
    MULTIPLY = 'MUL', 'ضریب'
    ADD = 'ADD', 'اضافه'
    MANUAL = 'MAN', 'دستی'


class ProductField(models.Model):
    title = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                             choices=FieldName.choices,
                             blank=False, null=False)
    filed_list = models.JSONField(default=dict,
                                  blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                blank=False, null=False,
                                related_name='product_field_list')
    price_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                  choices=FieldPriceType.choices, default=FieldPriceType.NONE,
                                  blank=False, null=False, verbose_name="Price Type")

    class Meta:
        ordering = ['-sort_number', 'product']
        verbose_name = 'Product Field'
        verbose_name_plural = 'Product Fields'

    def __str__(self):
        return f'Filed: #{self.title}: {self.product}'

    def face_method(self):
        face = FaceType.ONE
        self.detail = []

    def size_method(self):
        sizeable = True
        method = SizeMethod.FIX
        # counter = 0++
        self.detail = []

    def paper_method(self):
        self.detail = []

    def tirage_method(self):
        method = TirageMethod.FIX
        self.detail = []

    def copies_method(self):
        amount = 1
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

    def duration_method(self):
        self.detail = []


class Size(models.Model):
    name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(2)],
                            blank=False, null=False)
    display_name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(2)],
                            blank=False, null=False, verbose_name='Display Name')
    description = models.TextField(max_length=78,
                                   blank=True, null=True)
    length = models.FloatField(default=0,
                               blank=False, null=False)
    width = models.FloatField(default=0,
                              blank=False, null=False)
    base_cutting_edge = models.FloatField(default=0,
                                          blank=False, null=False, verbose_name='Base Cutting Edge')

    class Meta:
        ordering = ['display_name']
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'

    def __str__(self):
        return f'Size: {self.display_name}'


class SheetPaper(models.Model):
    material = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(2)],
                                blank=False, null=False)
    display_name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(2)],
                                    blank=False, null=False, verbose_name='Display Name')
    description = models.TextField(max_length=78, blank=True, null=True)
    length = models.FloatField(default=0,
                               blank=False, null=False)
    width = models.FloatField(default=0,
                              blank=False, null=False)
    weight = models.FloatField(default=0,
                                     blank=False, null=False)
    sheet_paper_number = models.PositiveSmallIntegerField(default=0,
                                                          blank=False, null=False, verbose_name='Sheet Paper Number')
    purchase_price = models.PositiveIntegerField(default=0,
                                            blank=False, null=False, verbose_name='Purchase Price')
    cutting_price = models.PositiveIntegerField(default=0,
                                                blank=False, null=False, verbose_name='Cutting Price')
    inventory = models.PositiveIntegerField(default=0,
                                            blank=False, null=False)

    class Meta:
        ordering = ['display_name']
        verbose_name = 'Sheet Paper'
        verbose_name_plural = 'Sheet Papers'

    def __str__(self):
        return f'Sheet Paper: {self.display_name}'


class Paper(models.Model):
    sheet_paper = models.ForeignKey(SheetPaper, on_delete=models.PROTECT,
                                    blank=False, null=False,
                                    related_name='paper_list')
    size = models.ForeignKey(Size, on_delete=models.PROTECT,
                             blank=False, null=False,
                             related_name='paper_list')
    per_paper_weight = models.FloatField(default=0,
                                         blank=False, null=False, verbose_name='Per-Paper Weight')
    inventory = models.PositiveIntegerField(default=0,
                                            blank=False, null=False)
    per_paper_price = models.PositiveIntegerField(default=0,
                                                  blank=False, null=False, verbose_name='Per-Paper Price')
    color_print_price = models.PositiveIntegerField(default=0,
                                                    blank=False, null=False, verbose_name='Color Print Price')
    baw_print_price = models.PositiveIntegerField(default=0,
                                                  blank=False, null=False, verbose_name='Baw Print Price')

    class Meta:
        ordering = ['sheet_paper']
        verbose_name = 'Paper'
        verbose_name_plural = 'Papers'

    def __str__(self):
        return f'Paper: {self.sheet_paper.display_name} #{self.size.display_name}'


class Tirage(models.Model):
    amount = models.PositiveSmallIntegerField(unique=True, blank=False, null=False)

    class Meta:
        ordering = ['amount']
        verbose_name = "Tirage"
        verbose_name_plural = "Tirages"

    def __str__(self):
        return f'Tirage #{self.amount}'


class Design(models.Model):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    base_price = models.PositiveIntegerField(default=0,
                                             blank=False, null=False, verbose_name='Base Price')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    avg_duration = models.PositiveSmallIntegerField(default=0,
                                                    blank=False, null=False, verbose_name='Average Duration')
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='design_list')
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # icon = models.ImageField(upload_to="ProductCategory/", blank=True, null=True)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)
    total_order = models.PositiveSmallIntegerField(default=0,
                                                   blank=False, null=False, verbose_name='Total Order')
    last_order = models.DateField(blank=True, null=True, verbose_name='Last Order')
    total_sale = models.PositiveIntegerField(default=0,
                                             blank=False, null=False, verbose_name='Total Sale')

    class Meta:
        ordering = ['-sort_number', 'category']
        verbose_name = "Design"
        verbose_name_plural = "Designs"

    def __str__(self):
        return f'Design #{self.pk}: {self.title}'


class Color(models.Model):
    name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    code = models.CharField(max_length=6, default='000', unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'

    def __str__(self):
        return f'#{self.code}: {self.name}'


class Banner(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    width = models.PositiveSmallIntegerField(default=0,
                                             blank=False, null=False)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    punch_price = models.PositiveIntegerField(default=0,
                                              blank=False, null=False, verbose_name='Punch Price')
    leaf_size = models.PositiveSmallIntegerField(default=0,
                                                 blank=False, null=False, verbose_name='Leaf Size')
    leaf_price = models.FloatField(default=0,
                                   blank=False, null=False, verbose_name='Leaf Price')
    white_price = models.FloatField(default=0,
                                    blank=False, null=False, verbose_name='White Price')
    # total_print = models.FloatField(default=0, blank=False, null=False, verbose_name="Total Print")
    # total_waste = models.FloatField(default=0, blank=False, null=False, verbose_name="Total Gap")
    # total_leaf = models.FloatField(default=0, blank=False, null=False, verbose_name="Total Leaf")
    # total_white = models.FloatField(default=0, blank=False, null=False, verbose_name="Total White")

    class Meta:
        ordering = ['title']
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

    def __str__(self):
        return f'{self.title}'


class OptionInputType(models.TextChoices):
    CHECKBOX = 'CHE', 'چک باکس'
    RADIOBUTTON = 'RAD', 'رادیو'
    WATERFALL = 'WAT', 'آبشاری'
    NUMBER = 'NUM', 'عدد'
    TEXTFIELD = 'TXF', 'متن'
    TEXTBOX = 'TXB', 'ناحیه متنی'
    DATE = 'DAT', 'تاریخ'
    FILE = 'FIL', 'فایل'


class OptionCategory(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    input_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                  choices=OptionInputType.choices,
                                  blank=False, null=False, verbose_name='Input Type')
    parent = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True,
                                related_name='sub_categories')
    # icon = models.ImageField(upload_to="services", blank=False, null=False)
    mandatory = models.BooleanField(default=False,
                                    blank=False, null=False)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    is_numberize = models.BooleanField(default=True,
                                       blank=False, null=False, verbose_name='Is Numberize')
    in_formula = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='In Formula')
    after_print = models.BooleanField(default=False,
                                      blank=False, null=False, verbose_name='After Print')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Option Category"
        verbose_name_plural = "Option Categories"

    def __str__(self):
        return f'Option Category: {self.title}'


class Option(models.Model):
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    category = models.ForeignKey(OptionCategory, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='option_list')
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    base_price = models.PositiveIntegerField(default=0,
                                             blank=False, null=False, verbose_name='Base Price')
    keyword = models.CharField(max_length=10, unique=True, validators=[validators.MinLengthValidator(3)],
                               blank=True, null=True)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')

    class Meta:
        ordering = ['-sort_number', 'category']
        verbose_name = 'Option'
        verbose_name_plural = 'Options'

    def __str__(self):
        return f'Option: {self.title}'


class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='option_list')
    option = models.ForeignKey(Option, on_delete=models.CASCADE,
                               related_name='product_list')
    price = models.PositiveIntegerField(blank=True, null=True)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=True, null=True, verbose_name='Sort Number')
    always_show = models.BooleanField(default=True,
                                      blank=False, null=False, verbose_name='Always Show')
    dependent_option = models.ManyToManyField('ProductOption')


    class Meta:
        ordering = ['product', 'option', '-sort_number']
        verbose_name = 'Product Option'
        verbose_name_plural = 'Product Options'

    def __str__(self):
        return f'{self.product}: {self.option}'


class PriceListCategory(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # icon = models.ImageField(upload_to="ProductCategory/", blank=True, null=True)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Price List Category'
        verbose_name_plural = 'Price List Categories'

    def __str__(self):
        return f'Price List Category: {self.title}'


class SizeUnit(models.TextChoices):
    CM = 'CM', 'سانتی متر'
    M = 'M', 'متر'


class PriceListTable(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    price_list_categories = models.ManyToManyField(
        PriceListCategory,
        through='PriceListTableCategory',
        through_fields=('table', 'category'),
        verbose_name='Price List Categories'
    )
    product_categories = models.ManyToManyField(
        ProductCategory,
        through='PriceListTableProductCategory',
        through_fields=('table', 'product_category'),
        verbose_name='Product Categories'
    )

    class Meta:
        verbose_name = 'Price List Table'
        verbose_name_plural = 'Price List Tables'

    def __str__(self):
        return f'Price List Table: {self.title}'


class PriceListTableCategory(models.Model):
    table = models.ForeignKey(PriceListTable, on_delete=models.CASCADE,
                             related_name='category_list')
    category = models.ForeignKey(PriceListCategory, on_delete=models.CASCADE,
                                 related_name='table_list')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    size_column = models.BooleanField(default=False,
                                      blank=False, null=False, verbose_name='Size Column')
    size_unit = models.CharField(max_length=2, validators=[validators.MinLengthValidator(1)],
                                 choices=SizeUnit.choices, default=SizeUnit.CM,
                                 blank=False, null=False, verbose_name='Size Unit')
    duration_column = models.BooleanField(default=False,
                                          blank=False, null=False, verbose_name='Duration Column')
    gallery_column = models.BooleanField(default=False,
                                         blank=False, null=False, verbose_name='Gallery Column')

    class Meta:
        ordering = ['category', 'table']
        verbose_name = "Price List Table Category"
        verbose_name_plural = "Price List Table Categories"

    def __str__(self):
        return f'{self.table} -in- {self.category}'


class PriceListTableProductCategory(models.Model):
    table = models.ForeignKey(PriceListTable, on_delete=models.CASCADE,
                              related_name='product_category_list')
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                         related_name='price_table_list')
    items = models.ManyToManyField(
        Product,
        through='PriceListTableProductItem',
        through_fields=('price_list', 'product'),
    )

    class Meta:
        ordering = ['product_category', 'table']
        verbose_name = 'Price List Table Product Category'
        verbose_name_plural = 'Price List Table Product Categories'

    def __str__(self):
        return f'{self.product_category} -in- {self.table}'


class PriceListTableProductItem(models.Model):
    price_list = models.ForeignKey(PriceListTableProductCategory, on_delete=models.CASCADE,
                                   related_name='product_list')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='price_table_list')
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    tirage_row = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='Tirage Row')

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Price List Table Product Item'
        verbose_name_plural = 'Price List Table Product Items'

    def __str__(self):
        return f'{self.product} -in- {self.price_list}'
