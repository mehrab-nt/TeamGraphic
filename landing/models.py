from django.db import models
from django.core import validators
from django.utils import timezone
from user.models import Role
from employee.models import Employee


class Metadata(models.Model):
    seo_title = models.CharField(max_length=60, unique=True, validators=[validators.MinLengthValidator(3)],
                                 blank=False, null=False, verbose_name='Seo title')
    seo_description = models.TextField(max_length=160, validators=[validators.MinLengthValidator(3)],
                                       blank=True, null=True, verbose_name='Seo description')
    seo_slug = models.SlugField(max_length=30, unique=True,
                                blank=False, null=False, verbose_name='Seo slug')
    canonical_link = models.URLField(blank=True, null=True, verbose_name='Canonical link')
    keywords = models.TextField(max_length=236, blank=True, null=True)
    no_index = models.BooleanField(default=False,
                                   blank=False, null=False, verbose_name='No index')
    redirect_303_link = models.URLField(blank=True, null=True, verbose_name='Redirect 303 link')

    class Meta:
        verbose_name = 'Metadata'
        verbose_name_plural = 'Metadata'

    def __str__(self):
        return f"Metadate: {self.seo_title}"


class LandingCategoryType(models.TextChoices):
    MAIN = 'MAN', 'صفحه اصلی'
    PAGE = 'PAG', 'صفحه ایستا'
    DOWNLOAD = 'DON', 'دانلود'
    ARTICLE = 'ART', 'مطلب'
    CATEGORY = 'CAT', 'دسته محصول'
    PRODUCT = 'PRO', 'محصول'


class LandingCategory(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    parent_category = models.ForeignKey('self', on_delete=models.PROTECT,
                                        blank=True, null=True, verbose_name='Parent Category',
                                        related_name='child_categories')
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=LandingCategoryType.choices, default=LandingCategoryType.PAGE,
                            blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    metadata = models.OneToOneField(Metadata, on_delete=models.PROTECT, blank=False, null=False,
                                    related_name="landing_category")
    is_landing = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='Is Landing')
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # icon = models.ImageField(upload_to="ProductCategory/", blank=True, null=True)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)

    class Meta:
        ordering = ['parent_category', '-sort_number']
        verbose_name = "Landing Category"
        verbose_name_plural = "Landing Categories"

    def __str__(self):
        return f"Landing Category: {self.title}"


class PageSize(models.TextChoices):
    DEFAULT = 'DEF', 'پیشفرض'
    FULL = 'FUL', 'تمام صفحه'
    HALF = 'HAF', 'نیم صفحه'


class Landing(models.Model):
    title = models.CharField(max_length=60, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    category = models.ForeignKey(LandingCategory, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='landing_list')
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    sort_number = models.IntegerField(default=0,
                                      blank=False, null=False, verbose_name='Sort Number')
    page_size = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                 choices=PageSize.choices, default=PageSize.DEFAULT,
                                 blank=False, null=False, verbose_name='Page Size')
    metadata = models.OneToOneField(Metadata, on_delete=models.PROTECT,
                                    blank=False, null=False,
                                    related_name="landing")
    writer_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                        blank=True, null=True, verbose_name='Writer Employee',
                                        related_name="write_landing_list")
    write_date = models.DateField(default=timezone.now,
                                  blank=False, null=False, verbose_name='Write Date')
    custom_style_class = models.CharField(max_length=23,
                                          blank=True, null=True, verbose_name='Custom Style Class')
    hide_header = models.BooleanField(default=False,
                                      blank=False, null=False, verbose_name='Hide Header')
    hide_footer = models.BooleanField(default=False,
                                      blank=False, null=False, verbose_name='Hide Footer')
    # file = models.FileField(upload_to="files", blank=True, null=True)
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # icon = models.ImageField(upload_to="ProductCategory/", blank=True, null=True)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)

    class Meta:
        ordering = ['category', '-sort_number']
        verbose_name = "Landing"
        verbose_name_plural = "Landings"

    def __str__(self):
        return f"Landing: {self.title}"


class SectionType(models.TextChoices):
    BANNER = 'BAN', 'بنر'
    HEAD = 'HED', 'عنوان'
    CATEGORY = 'CAT', 'دسته بندی'
    INFO = 'INF', 'اطلاعات محصول'
    GALLERY = 'GAL', 'گالری'
    VIDEO = 'VID', 'ویدیو'
    BRIEF = 'BRF', 'معرفی'
    CONTENT = 'CON', 'محتوا'
    QUESTION = 'QUS', 'سوالات متداول'
    TABLE = 'TBL', 'جدول قیمت'
    PARENT = 'PAR', 'لندینگ مادر'
    FREE = 'FRE', 'آزاد'


class Section(models.Model):
    section_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                    choices=SectionType.choices, default=SectionType.FREE,
                                    verbose_name='Section Type',
                                    blank=False, null=False)
    section_order = models.IntegerField(default=0,
                                        blank=False, null=False, verbose_name="Section Order")
    landing = models.ForeignKey(Landing, on_delete=models.CASCADE,
                                blank=False, null=False,
                                related_name="sections_list")
    elements = models.JSONField(default=dict, blank=False, null=False)

    class Meta:
        ordering = ['landing', '-section_order']
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return f"Section #{self.section_order} /For: {self.landing}"


class VisualMenuType(models.TextChoices):
    SLIDESHOW = 'SLI', 'اسلاید شو'
    TIMER_GALLERY = 'TIM', 'گالری زماندار'
    IMAGE_BOX = 'BOX', 'باکس تصویر'


class VisualMenu(models.Model):
    title = models.CharField(max_length=78, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=VisualMenuType.choices,
                            blank=False, null=False)
    # image1 = models.ImageField(upload_to="images/", blank=False, null=False)
    # image2 = models.ImageField(upload_to="images/", blank=False, null=False)
    # image3 = models.ImageField(upload_to="images/", blank=False, null=False)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)
    is_linked = models.BooleanField(default=False,
                                    blank=False, null=False, verbose_name='Is Linked')
    hyperlink = models.URLField(blank=True, null=True)
    landing = models.ForeignKey(Landing, on_delete=models.PROTECT, blank=True, null=True,
                                related_name='linked_visual_menu_list')
    sort_number = models.IntegerField(default=0,
                                      blank=False, null=False, verbose_name='Sort Number')
    fields = models.JSONField(default=dict,
                              blank=False, null=False)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')

    class Meta:
        ordering = ['-sort_number', '-type']
        verbose_name = "Visual Menu"
        verbose_name_plural = "Visual Menus"

    def __str__(self):
        return f"{self.type} #{self.sort_number}: {self.title}"
