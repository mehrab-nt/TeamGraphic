from django.db import models
from django.core import validators
from mptt.models import MPTTModel, TreeForeignKey
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


class ProductCategory(MPTTModel):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    product_description = models.TextField(max_length=236,
                                           blank=True, null=True, verbose_name='Product Description')
    parent_category = TreeForeignKey('self', on_delete=models.CASCADE,
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
    gallery = models.ForeignKey('GalleryCategory', on_delete=models.SET_NULL,
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

    class MPTTMeta:
        order_insertion_by = ['sort_number', 'title']
        parent_attr = 'parent_category'

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        if getattr(self, "_skip_custom_save", False):
            return super().save(*args, **kwargs)
        if self.image and not self.alt:
            self.alt = f'{self.title}عکس دسته محصولات '
        if self.fast_order and not self.fast_order_title:
            self.fast_order_title = self.title
        if self.landing:
            self.is_landing = True
        if self.parent_category:
            if self == self.parent_category:
                raise ValidationError("دسته بندی نمی تواند زیرمجموعه خودش باشد")
            if self.pk and self.parent_category.is_descendant_of(self):
                raise ValidationError("نمی توان دسته زیرمجموعه را به عنوان دسته بالاتر انتخاب کرد")
        return super().save(*args, **kwargs)

    def clean(self): # MEH: Prevent circular reference A → B → C → A in Admin Panel
        if self.parent_category:
            if self == self.parent_category:
                raise ValidationError("A category cannot be its own parent.")
            if self.pk and self.parent_category.is_descendant_of(self):
                raise ValidationError("You cannot assign a descendant as the parent category.")

    def update_all_subcategories_and_items(self): # MEH: Call when update status of a category
        new_status = self.status
        descendants = self.get_descendants()
        descendants.update(status=new_status)
        Product.objects.filter(parent_category__in=[self] + list(descendants)).update(status=new_status)

    def get_slug_path(self):
        return ' - '.join(
            [cat.title for cat in self.get_ancestors(include_self=True)]
        )


class ProductType(models.TextChoices):
    OFFSET = 'OFF', 'افست'
    LARGE_FORMAT = 'LAR', 'لارج فرمت'
    DIGITAL = 'DIG', 'دیجیتال'
    SOLID = 'SLD', 'محصول عمومی'

class GalleryType(models.TextChoices):
    SHOW = 'SHO', 'نمایش'
    OPTIONAL = 'OPT', 'قابل انتخاب'
    MANDATARY = 'MAN', 'اجباری'


class Product(models.Model):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=ProductType.choices,
                            blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    category_description = models.BooleanField(default=True,
                                               blank=False, null=False, verbose_name='Category Description')
    parent_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                        blank=True, null=True,
                                        related_name='product_list')
    image = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='image_for_products')
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=True, null=False)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    template = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name='template_for_products')
    gallery = models.ForeignKey('GalleryCategory', on_delete=models.SET_NULL,
                                blank=True, null=True,
                                related_name='gallery_for_products')
    gallery_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                    choices=GalleryType.choices,
                                    blank=True, null=True)
    status = models.CharField(max_length=2, validators=[validators.MinLengthValidator(2)],
                              choices=ProductStatus.choices, default=ProductStatus.ACTIVE,
                              blank=False, null=False)
    is_private = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='Is Private')
    accounting_id = models.PositiveBigIntegerField(default=0,
                                                   blank=True, null=True, verbose_name='Accounting ID')
    accept_copies = models.BooleanField(default=True,
                                        blank=False, null=False, verbose_name='Accept Copies')
    min_copies = models.PositiveSmallIntegerField(default=1,
                                                  blank=False, null=False, verbose_name='Min Copies')
    designs = models.ManyToManyField('Design', blank=True,
                                    related_name='design_for_products')
    files = models.ManyToManyField('ProductFileField', blank=True,
                                   related_name='file_for_products')
    check_file = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='Check File')
    options = models.ManyToManyField(
        'Option',
        through='ProductOption',
        through_fields=('product', 'option')
    )
    total_order = models.PositiveIntegerField(default=0,
                                              blank=False, null=False, verbose_name='Total Order')
    last_order = models.DateField(blank=True, null=True, verbose_name='Last Order')
    total_main_sale = models.PositiveIntegerField(default=0,
                                                  blank=False, null=False, verbose_name='Total Main Sale')
    total_option_sale = models.PositiveIntegerField(default=0,
                                                    blank=False, null=False, verbose_name='Total Option Sale')

    class Meta:
        ordering = ('parent_category', 'sort_number')
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f'TGP-{self.pk}: {self.title}'

    def save(self, *args, **kwargs):
        if self.image and not self.alt:
            self.alt = f'{self.title}عکس محصول '
        super().save(*args, **kwargs)

    def get_category_path(self):
        return self.parent_category.get_slug_path()


class SizeMethod(models.TextChoices):
    FIXED_ONE = 'FIX', 'ثابت'
    FIXED_MULTIPLE = 'MUL', 'ثابت انتخابی'
    CUSTOM_INPUT = 'CUS', 'دلخواه'
    SUGGESTED_AND_CUSTOM = 'COM', 'پیشنهادی و دلخواه'


class OffsetProduct(models.Model):
    """
    MEH: Offset Product related models
    """
    product_info = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True,
                                        blank=False, null=False, verbose_name='Product Info',
                                        related_name='offset_info')
    one_face = models.BooleanField(default=True,
                                   blank=False, null=False, verbose_name='One Face')
    tow_face = models.BooleanField(default=True,
                                   blank=False, null=False, verbose_name='Tow Face')
    size_method = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                   choices=SizeMethod.choices, default=SizeMethod.FIXED_ONE)
    min_max_size = models.JSONField(default=dict,
                                    blank=True, null=True, verbose_name='Min & Max Size')
    size_list = models.ManyToManyField('Size', blank=False)
    tirage_list = models.ManyToManyField('Tirage', blank=False)
    page_list = models.ManyToManyField('Page', blank=True)
    duration_list = models.ManyToManyField('Duration', blank=False)
    folding_list = models.ManyToManyField('Folding', blank=True)
    manual_price = models.JSONField(default=dict,
                                    blank=True, null=True, verbose_name='Manual Price')


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
    lat = models.BooleanField(default=False,
                              blank=False, null=False)

    class Meta:
        ordering = ['display_name']
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'

    def __str__(self):
        return f'Size: {self.display_name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        paper_list = self.paper_list.all()
        for paper in paper_list:
            paper.save()


class Tirage(models.Model):
    amount = models.PositiveSmallIntegerField(unique=True, blank=False, null=False)

    class Meta:
        ordering = ['amount']
        verbose_name = "Tirage"
        verbose_name_plural = "Tirages"

    def __str__(self):
        return f'Tirage #{self.amount}'


class Page(models.Model):
    number = models.PositiveSmallIntegerField(unique=True, blank=False, null=False)

    class Meta:
        ordering = ['number']
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return f'Tirage #{self.number}'


class Duration(models.Model):
    title = models.CharField(max_length=78, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    day = models.PositiveSmallIntegerField(blank=False, null=False)
    before_12 = models.BooleanField(default=False)

    class Meta:
        ordering = ['day']
        verbose_name = "Duration"
        verbose_name_plural = "Durations"

    def __str__(self):
        return f'Duration #{self.title}'


class LargeFormatProduct(models.Model):
    """
    MEH: Large Format Product related models
    """
    product_info = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True,
                                        blank=False, null=False, verbose_name='Product Info',
                                        related_name='large_format_info')
    min_width = models.PositiveSmallIntegerField(default=100,
                                                 blank=False, null=False, verbose_name='Min Width')
    min_height = models.PositiveSmallIntegerField(default=100,
                                                  blank=False, null=False, verbose_name='Min Height')
    banner_list = models.ManyToManyField('Banner', blank=False)
    print_price = models.PositiveSmallIntegerField(default=0,
                                                   blank=False, null=False, verbose_name='Print Price')
    waste_price = models.PositiveSmallIntegerField(default=0,
                                                   blank=False, null=False, verbose_name='Waste Price')
    gap_price = models.PositiveSmallIntegerField(default=0,
                                                 blank=False, null=False, verbose_name='Gap Price')

    punch_price = models.PositiveSmallIntegerField(default=0,
                                                   blank=False, null=False, verbose_name='Punch Price')
    leaf_size = models.PositiveSmallIntegerField(default=0,
                                                 blank=False, null=False, verbose_name='Leaf Amount')
    leaf_price = models.PositiveSmallIntegerField(default=0,
                                                  blank=False, null=False, verbose_name='Leaf Price')
    print_length_discount = models.JSONField(default=dict,
                                             blank=True, null=True, verbose_name='Print Length Discount')

    def save(self, *args, **kwargs):
        if self.print_price and not self.waste_price:
            self.waste_price = self.print_price
        if self.waste_price and not self.gap_price:
            self.gap_price = self.waste_price
        super().save()


class Banner(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    width = models.PositiveSmallIntegerField(default=0,
                                             blank=False, null=False)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    total_print = models.FloatField(default=0, blank=False, null=False, verbose_name="Total Print")
    total_waste = models.FloatField(default=0, blank=False, null=False, verbose_name="Total Waste")
    total_leaf = models.FloatField(default=0, blank=False, null=False, verbose_name="Total Leaf")
    total_gap = models.FloatField(default=0, blank=False, null=False, verbose_name="Total Gap")

    class Meta:
        ordering = ['title']
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

    def __str__(self):
        return f'{self.title}'


class SolidProduct(models.Model):
    """
    MEH: Solid Product related models
    """
    product_info = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True,
                                        blank=False, null=False, verbose_name='Product Info',
                                        related_name='solid_info')
    brief_information = models.JSONField(default=dict,
                                         blank=True, null=True, verbose_name='Brief Information')
    color_inventory_list = models.JSONField(default=dict,
                                            blank=False, null=False, verbose_name='Color Inventory List')
    sizable = models.BooleanField(default=False,
                                  blank=False, null=False)
    size_price = models.BooleanField(default=False,
                                     blank=False, null=False)
    min_max_size = models.JSONField(default=dict,
                                    blank=True, null=True, verbose_name='Min & Max Size')


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


class DigitalProduct(models.Model):
    """
    MEH: Digital Product related models
    """
    product_info = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True,
                                        blank=False, null=False, verbose_name='Product Info',
                                        related_name='digital_info')
    one_face = models.BooleanField(default=True,
                                   blank=False, null=False, verbose_name='One Face')
    tow_face = models.BooleanField(default=True,
                                   blank=False, null=False, verbose_name='Tow Face')
    pageable = models.BooleanField(default=False,
                                   blank=False, null=False)
    size_method = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                   choices=SizeMethod.choices, default=SizeMethod.FIXED_ONE)
    size_list = models.ManyToManyField('Size', blank=False)
    min_max_size = models.JSONField(default=dict,
                                    blank=True, null=True, verbose_name='Min & Max Size')
    min_tirage = models.PositiveSmallIntegerField(default=1,
                                                  blank=False, null=False, verbose_name='Min Tirage')
    max_tirage = models.PositiveSmallIntegerField(default=1000,
                                                  blank=False, null=False, verbose_name='Max Tirage')
    paper_list = models.ManyToManyField('Paper', blank=False,
                                        related_name='paper_list_for_digital')
    cover_paper_list = models.ManyToManyField('Paper', blank=True,
                                              related_name='paper_list_for_digital_cover')
    folding_list = models.ManyToManyField('Folding', blank=True)
    formula = models.TextField(max_length=1378, blank=True, null=True)


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        paper_list = self.paper_list.all()
        for paper in paper_list:
            paper.save()


class Paper(models.Model):
    sheet_paper = models.ForeignKey(SheetPaper, on_delete=models.PROTECT,
                                    blank=False, null=False,
                                    related_name='paper_list')
    size = models.ForeignKey(Size, on_delete=models.PROTECT,
                             blank=False, null=False,
                             related_name='paper_list')
    inventory = models.PositiveIntegerField(default=0,
                                            blank=False, null=False)
    per_paper_price = models.PositiveIntegerField(default=0,
                                                  blank=False, null=False, verbose_name='Per-Paper Price')
    color_print_price = models.PositiveIntegerField(default=0,
                                                    blank=False, null=False, verbose_name='Color Print Price')
    baw_print_price = models.PositiveIntegerField(default=0,
                                                  blank=False, null=False, verbose_name='Baw Print Price')
    cutting_price = models.PositiveSmallIntegerField(default=0,
                                                     blank=False, null=False, verbose_name='Cutting Price')
    folding_price = models.PositiveSmallIntegerField(default=0,
                                                     blank=False, null=False, verbose_name='Folding Price')

    class Meta:
        ordering = ['sheet_paper']
        verbose_name = 'Paper'
        verbose_name_plural = 'Papers'

    def __str__(self):
        return f'Paper: {self.sheet_paper.display_name} #{self.size.display_name}'

    def save(self, *args, **kwargs):
        self.per_paper_price = self.calculate_paper_price_per_size()
        super().save(*args, **kwargs)

    def calculate_paper_price_per_size(self):
        fit_along_length = self.sheet_paper.length // self.size.length
        fit_along_width = self.sheet_paper.width //  self.size.width
        rotated_fit_along_length = self.sheet_paper.length //  self.size.width
        rotated_fit_along_width = self.sheet_paper.width //  self.size.length
        total_fit = max(
            fit_along_length * fit_along_width,
            rotated_fit_along_length * rotated_fit_along_width
        )
        if total_fit == 0:
            return 0  # MEH: can't cut this size from the sheet
        price_per_piece = self.sheet_paper.purchase_price / self.sheet_paper.sheet_paper_number / total_fit
        price_per_piece += self.sheet_paper.cutting_price / self.sheet_paper.sheet_paper_number / total_fit
        return price_per_piece # MEH: Calculated base price per piece


class Folding(models.Model):
    folding_number = models.PositiveSmallIntegerField(default=1,
                                                      blank=False, null=False, verbose_name='Folding Number')
    title = models.CharField(max_length=78,
                             blank=False, null=False)
    description = models.TextField(max_length=236, blank=True, null=True)
    icon = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                             blank=True, null=True,
                             related_name='icon_for_lats')


class FileColorMode(models.TextChoices):
    CMYK = 'CMYK', 'CMYK'
    RGB = 'RGB', 'RGB'
    BOTH = 'BOTH', 'هر دو'

class FileType(models.TextChoices):
    JPEG = 'JPEG', 'JPEG'
    JPG = 'JPG', 'JPG'
    TIF = 'TIF', 'TIF'
    ZIP = 'ZIP', 'ZIP'
    RAR = 'RAR', 'RAR'
    PDF = 'PDF', 'PDF'
    PSD = 'PSD', 'PSD'
    CDR = 'CDR', 'CDR'
    AI = 'AI', 'AI'
    EPS = 'EPS', 'EPS'


class ProductFileField(models.Model):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    depend_on = models.ForeignKey('self', on_delete=models.PROTECT,
                                  blank=True, null=True,
                                  related_name='child_file_list')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    color_mode = models.CharField(max_length=4, validators=[validators.MinLengthValidator(3)],
                                  choices=FileColorMode.choices,
                                  blank=True, null=True, verbose_name='Color Mode')
    resolution = models.PositiveSmallIntegerField(default=300,
                                                  blank=False, null=False)
    mandatory = models.BooleanField(default=False,
                                    blank=False, null=False)
    accept_type = models.JSONField(default=dict,
                                   blank=False, null=False, verbose_name='Accept Type')

    class Meta:
        ordering = ['sort_number', 'title']
        verbose_name = 'Product File'
        verbose_name_plural = 'Product Files'

    def __str__(self):
        return f'{self.title}'

    def clean(self): # MEH: Prevent circular reference A → B → C → A in Admin Panel
        current = self.depend_on
        while current:
            if current == self:
                raise ValidationError(TG_PREVENT_CIRCULAR_CATEGORY)
            current = current.depend_on


class DesignVariantType(models.TextChoices):
    FACE = 'FAC', 'وجه'
    LAT = 'LAT', 'لت'
    PAGE = 'PAG', 'صفحه'


class Design(models.Model):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    base_price = models.PositiveIntegerField(default=0,
                                             blank=False, null=False, verbose_name='Base Price')
    second_price = models.PositiveIntegerField(default=0,
                                               blank=True, null=True, verbose_name='Second Price')
    variant_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                    choices=DesignVariantType.choices,
                                    blank=True, null=True, verbose_name='Variant Type')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    avg_duration = models.PositiveSmallIntegerField(default=0,
                                                    blank=False, null=False, verbose_name='Average Duration')
    category = models.ManyToManyField(ProductCategory, blank=False,
                                      related_name='design_list')
    image = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='image_for_designs')
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=True, null=False)
    total_order = models.PositiveSmallIntegerField(default=0,
                                                   blank=False, null=False, verbose_name='Total Order')
    last_order = models.DateField(blank=True, null=True, verbose_name='Last Order')
    total_sale = models.PositiveIntegerField(default=0,
                                             blank=False, null=False, verbose_name='Total Sale')

    class Meta:
        ordering = ['sort_number']
        verbose_name = "Design"
        verbose_name_plural = "Designs"

    def __str__(self):
        return f'Design #{self.pk}: {self.title}'

    def save(self, *args, **kwargs):
        if self.image and not self.alt:
            self.alt = f'{self.title}عکس طراحی '
        super().save(*args, **kwargs)


class OptionInputType(models.TextChoices):
    CHECKBOX = 'CHE', 'چک باکس'
    RADIOBUTTON = 'RAD', 'رادیو'
    WATERFALL = 'WAT', 'آبشاری'
    NUMBER = 'NUM', 'عدد'
    TEXTFIELD = 'TXF', 'متن'
    TEXTBOX = 'TXB', 'ناحیه متنی'
    DATE = 'DAT', 'تاریخ'
    FILE = 'FIL', 'فایل'


class OptionCategory(MPTTModel):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    product_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                    choices=ProductType.choices, default=None,
                                    blank=True, null=True)
    input_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                  choices=OptionInputType.choices,
                                  blank=False, null=False, verbose_name='Input Type')
    parent_category = TreeForeignKey('self', on_delete=models.CASCADE,
                                     blank=True, null=True, verbose_name='Parent Category',
                                     related_name='sub_categories')
    icon = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                             blank=True, null=True,
                             related_name='icon_for_options')
    mandatory = models.BooleanField(default=False,
                                    blank=False, null=False)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    in_formula = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='In Formula')
    keyword = models.CharField(max_length=23, unique=True,
                               blank=False, null=False)
    after_print = models.BooleanField(default=False,
                                      blank=False, null=False, verbose_name='After Print')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')

    class Meta:
        ordering = ['sort_number']
        verbose_name = "Option Category"
        verbose_name_plural = "Option Categories"

    class MPTTMeta:
        order_insertion_by = ['sort_number', 'title']
        parent_attr = 'parent_category'

    def __str__(self):
        return f'Option Category: {self.title}'

    def clean(self): # MEH: Prevent circular reference A → B → C → A in Admin Panel
        if self.parent_category:
            if self == self.parent_category:
                raise ValidationError("A category cannot be its own parent.")
            if self.pk and self.parent_category.is_descendant_of(self):
                raise ValidationError("You cannot assign a descendant as the parent category.")

    def update_all_subcategories_and_items(self): # MEH: Call when update is_active of a category
        new_is_active = self.is_active
        descendants = self.get_descendants()
        descendants.update(is_active=new_is_active)
        Option.objects.filter(parent_category__in=[self] + list(descendants)).update(is_active=new_is_active)

    def get_slug_path(self):
        return ' - '.join(
            [cat.title for cat in self.get_ancestors(include_self=True)]
        )


class PriceAmountType(models.TextChoices):
    PERCENT = 'PER', 'درصدی'
    FIX = 'FIX', 'ثابت'


class Option(models.Model):
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    parent_category = models.ForeignKey(OptionCategory, on_delete=models.CASCADE,
                                        blank=False, null=False,
                                        related_name='option_list')
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    is_numberize = models.BooleanField(default=True,
                                       blank=False, null=False, verbose_name='Is Numberize')
    base_amount = models.FloatField(default=0,
                                    blank=False, null=False, verbose_name='Base Amount')
    price_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                  choices=PriceAmountType.choices, default=PriceAmountType.FIX)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')

    class Meta:
        ordering = ['parent_category', 'sort_number']
        verbose_name = 'Option'
        verbose_name_plural = 'Options'

    def __str__(self):
        return f'Option: {self.title}'


class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='option_list')
    option = models.ForeignKey(Option, on_delete=models.CASCADE,
                               related_name='product_list')
    base_multiply = models.FloatField(blank=True, null=True)
    count_discount = models.JSONField(default=dict,
                                      blank=True, null=True, verbose_name='Tirage Discount')
    always_show = models.BooleanField(default=True,
                                      blank=False, null=False, verbose_name='Always Show')
    dependent_option = models.ManyToManyField('Option', blank=True,
                                              related_name='child_option_list')

    class Meta:
        ordering = ['product', 'option']
        verbose_name = 'Product Option'
        verbose_name_plural = 'Product Options'
        unique_together = ('product', 'option')

    def __str__(self):
        return f'{self.product}: {self.option}'

    def clean(self): # MEH: just for make sure valid data from django Admin panel
        super().clean()
        if not self.option_id:
            return  # MEH: Skip if not fully initialized

        def has_cycle(current_id, visited):
            if current_id in visited:
                return True
            visited.add(current_id)
            deps = ProductOption.objects.filter(product=self.product, option_id=current_id).values_list('dependent_option__id', flat=True)
            for dep_id in deps:
                if dep_id == self.option_id:  # MEH: direct cycle
                    return True
                if has_cycle(dep_id, visited.copy()):
                    return True
            return False

        for dep in self.dependent_option.all():
            if dep.id == self.option_id:
                raise ValidationError("Option cannot depend on itself.")
            if has_cycle(dep.id, {self.option_id}):
                raise ValidationError(f"Circular dependency detected via Option {dep.id}.")

    @staticmethod
    def detect_cycle(dependency_map): # MEH: Detects cycles in a dependency graph represented as a dict: { option_id: [dependent_option_ids] }
        visited = set()
        stack = set()

        def dfs(option_id):
            if option_id in stack:
                return True  # MEH: Cycle detected
            if option_id in visited:
                return False
            visited.add(option_id)
            stack.add(option_id)
            for dep in dependency_map.get(option_id, []):
                if dfs(dep):
                    return True
            stack.remove(option_id)
            return False

        for opt_id in dependency_map:
            if dfs(opt_id):
                return True
        return False # MEH: It's ok


class GalleryCategory(MPTTModel):
    name = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    parent_category = TreeForeignKey('self', on_delete=models.CASCADE,
                                     blank=True, null=True,
                                     related_name='sub_galleries')

    class Meta:
        ordering = ['sort_number', 'name']
        verbose_name = 'Gallery Category'
        verbose_name_plural = 'Gallery Categories'

    class MPTTMeta:
        order_insertion_by = ['sort_number', 'name']
        parent_attr = 'parent_category'

    def __str__(self):
        if self.parent_category:
            return f"{self.parent_category}/{self.name}/"
        else:
            return f"{self.name}"

    def clean(self): # MEH: Prevent circular reference A → B → C → A in Admin Panel
        if self.parent_category:
            if self == self.parent_category:
                raise ValidationError("A category cannot be its own parent.")
            if self.pk and self.parent_category.is_descendant_of(self):
                raise ValidationError("You cannot assign a descendant as the parent category.")

    def get_slug_path(self):
        return ' - '.join(
            [category.name for category in self.get_ancestors(include_self=True)]
        )


def get_random_basename(instance): # MEH: With this image and thumbnail get equal name
    if not hasattr(instance, "_random_basename"):
        instance._random_basename = uuid.uuid4().hex[:8]
    return instance._random_basename

def gallery_preview_image_path(instance, filename): # MEH: Create a dir for thumbnail in each folder
    base_name = get_random_basename(instance)
    filename = f"thumb-{base_name}.webp"
    return f'gallery/thumbnails/{filename}'

def gallery_upload_image_path(instance, filename): # MEH: Upload File here (with safe slug name)
    base_name = get_random_basename(instance)
    filename = f"{base_name}.{instance.type}"
    return f'gallery/{filename}'


class GalleryImage(models.Model):
    name = models.CharField(max_length=78, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    type = models.CharField(max_length=5, validators=[validators.MinLengthValidator(1)],
                            blank=True, null=False)
    preview = models.ImageField(upload_to=gallery_preview_image_path, blank=True, null=True)
    image_file = models.FileField(upload_to=gallery_upload_image_path, blank=False, null=False)
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    parent_category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE,
                                        blank=True, null=True,
                                        related_name='sub_images')

    class Meta:
        ordering = ['sort_number', 'parent_category']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def __str__(self):
        return f'Image #{self.pk}: {self.name}'

    def save(self, *args, **kwargs):
        filename = self.image_file.name.split('/')[-1]
        name, ext = os.path.splitext(filename)
        if not self.name:
            self.name = name
        self.type = ext.lstrip('.').lower()
        if self.type.lower() in ['jpg', 'jpeg', 'png', 'webp']: # MEH: Just save image type file!
            if not self.preview:
                self.preview = create_square_thumbnail(self.image_file, size=(128, 128))
            super().save(*args, **kwargs)

    @property
    def full_image_name(self):
        return f'{self.name}.{self.type}'

    def get_download_url(self):
        return self.image_file.url


class PriceListCategory(MPTTModel):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    parent_category = TreeForeignKey('self', on_delete=models.CASCADE,
                                     blank=True, null=True, verbose_name="Parent Category",
                                     related_name='sub_categories')
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    image = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='image_for_price_list_categories')
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=True, null=False)

    class Meta:
        ordering = ['sort_number']
        verbose_name = 'Price List Category'
        verbose_name_plural = 'Price List Categories'

    class MPTTMeta:
        order_insertion_by = ['sort_number', 'title']
        parent_attr = 'parent_category'

    def __str__(self):
        return f'Price List Category: {self.title}'

    def clean(self): # MEH: Prevent circular reference A → B → C → A in Admin Panel
        if self.parent_category:
            if self == self.parent_category:
                raise ValidationError("A category cannot be its own parent.")
            if self.pk and self.parent_category.is_descendant_of(self):
                raise ValidationError("You cannot assign a descendant as the parent category.")

    def update_all_subcategories_and_items(self): # MEH: Call when update is_active of a category
        new_is_active = self.is_active
        descendants = self.get_descendants()
        descendants.update(is_active=new_is_active)
        PriceListTable.objects.filter(price_list_categories__in=[self] + list(descendants)).update(is_active=new_is_active)

    def get_slug_path(self):
        return ' - '.join(
            [cat.title for cat in self.get_ancestors(include_self=True)]
        )

    def delete(self, *args, **kwargs):
        table_deleted_count = self.delete_recursive()
        deleted_count, _ = super().delete(*args, **kwargs)
        return table_deleted_count + deleted_count, _

    def delete_recursive(self):
        deleted_count = 0
        related_items = list(self.sub_price_list_tables.all())
        for item in related_items:
            item.delete()
            deleted_count += 1
        return deleted_count


class SizeUnit(models.TextChoices):
    CM = 'CM', 'سانتی متر'
    M = 'M', 'متر'

class Label(models.TextChoices):
    DURATION = 'DUR', 'تحویل کاری'
    MANUAL = 'MAN', 'دستی'

class Column(models.TextChoices):
    SIZE = 'SIZ', 'ابعاد'
    PAPER = 'PAP', 'جنس کاغذ'
    PRODUCT = 'PRO', 'محصول'
    CATEGORY = 'CAT', 'دسته بندی'
    FACE = 'FAC', 'وجه'
    TIRAGE = 'TIR', 'تیراژ'
    DURATION = 'DUR', 'تحویل کاری'


class PriceListTable(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    image = models.ForeignKey(FileItem, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='image_for_price_list')
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=True, null=False)
    price_list_categories = models.ManyToManyField(PriceListCategory,
                                                   blank=True, verbose_name='Price List Categories',
                                                   related_name='sub_price_list_tables')
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                         blank=False, null=False, verbose_name='Product Category',
                                         related_name='for_price_list_tables')
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=ProductType.choices,
                            blank=False, null=False)
    product_list = models.ManyToManyField('Product',
                                          blank=True, verbose_name='Product List',
                                          related_name='in_price_table')
    sort_number = models.PositiveSmallIntegerField(default=0,
                                                   blank=False, null=False, verbose_name='Sort Number')
    size_unit = models.CharField(max_length=2, validators=[validators.MinLengthValidator(1)],
                                 choices=SizeUnit.choices, default=SizeUnit.CM,
                                 blank=False, null=False, verbose_name='Size Unit')
    gallery_column = models.BooleanField(default=False,
                                         blank=False, null=False, verbose_name='Gallery Column')
    label = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                blank=True, null=True,
                                choices=Label.choices)
    side_bar = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                blank=True, null=True, verbose_name='Side Bar',
                                choices=Column.choices)
    label_text = models.CharField(max_length=23,
                                  blank=True, null=True, verbose_name='Label Text')
    col_1 = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                             blank=True, null=True,
                             choices=Column.choices)
    col_2 = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                             blank=True, null=True,
                             choices=Column.choices)
    col_3 = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                             blank=True, null=True,
                             choices=Column.choices)
    show_category = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Price List Table'
        verbose_name_plural = 'Price List Tables'

    def __str__(self):
        return f'Price List Table: {self.title}'

    def save(self, *args, **kwargs):
        if self.image and not self.alt:
            self.alt = f'{self.title}عکس لیست قیمت '
        values = [
            self.side_bar,
            self.label,
            self.col_1,
            self.col_2,
            self.col_3,
        ]
        filtered_values = [v for v in values if v]
        if len(filtered_values) != len(set(filtered_values)):
            raise ValidationError("Duplicate values found in side_bar, label, or columns fields")
        super().save(*args, **kwargs)
