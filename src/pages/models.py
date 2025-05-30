from django.db import models
from django.core import validators
from django.utils import timezone
from users.models import Role, Employee


class PageSize(models.TextChoices):
    DEFAULT = "پیشفرض"
    FULL = "تمام صفحه"


class MainPage(models.Model):
    company_name = models.CharField(max_length=73, unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=23, unique=True, blank=True, null=True)
    # header_logo = models.ImageField(upload_to='logo', blank=True, null=True)
    # social_logo = models.ImageField(upload_to='logo', blank=True, null=True)
    # footer_logo = models.ImageField(upload_to='logo', blank=True, null=True)
    # fav_icon = models.ImageField(upload_to='logo', blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    social_media = models.JSONField(default=dict, blank=True, null=True)
    address = models.TextField(max_length=300, blank=True, null=True)
    wellcome_massage = models.TextField(max_length=300, blank=True, null=True)
    login_massage = models.TextField(max_length=300, blank=True, null=True)
    page_size = models.CharField(max_length=10, choices=PageSize.choices, default=PageSize.DEFAULT,
                                 blank=False, null=False)
    rules_page = models.ForeignKey('Landing', blank=True, null=True, on_delete=models.SET_NULL)
    rules_page_check = models.BooleanField(default=False, blank=False, null=False)
    about_me = models.TextField(max_length=1092, blank=True, null=True)
    metadate = models.ForeignKey('Metadata', on_delete=models.SET_NULL, blank=True, null=True)
    google_code = models.CharField(max_length=23, blank=True, null=True)
    google_code_type = models.CharField(max_length=3, blank=True, null=True)
    robot = models.TextField(max_length=1092, blank=True, null=True)
    redirect_list = models.JSONField(blank=True, null=True)


class Metadata(models.Model):
    seo_title = models.CharField(max_length=100, unique=True, validators=[validators.MinLengthValidator(3)],
                                 blank=False, null=False)
    seo_description = models.TextField(max_length=150, validators=[validators.MinLengthValidator(10)], blank=True, null=True)
    seo_slug = models.SlugField(max_length=100, unique=True, blank=False, null=False)
    canonical_link = models.URLField(blank=True, null=True)
    keywords = models.TextField(max_length=300, blank=True, null=True)
    no_index = models.BooleanField(default=False, blank=False, null=False)
    no_index_child = models.BooleanField(default=False, blank=False, null=False)
    # اگر دسته زیر مجموعه هر قسمتی از متا دیتاش خالی بود از اولین دسته بالاتر پر بشه
    parent_metadata = models.BooleanField(default=False, blank=False, null=False)
    redirect_303 = models.BooleanField(default=False, blank=False, null=False)
    redirect_303_link = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Metadata"
        verbose_name_plural = "Metadata"

    def __str__(self):
        return f"Metadate: {self.seo_title}"


class Landing(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    category = models.ForeignKey('LandingCategory', on_delete=models.PROTECT, blank=False, null=False,
                                 related_name="landing_list")
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")
    sort_number = models.IntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    page_size = models.CharField(max_length=10, choices=PageSize.choices, default=PageSize.DEFAULT,
                                 blank=False, null=False)
    metadata = models.OneToOneField(Metadata, on_delete=models.PROTECT, blank=False, null=False,
                                    related_name="metadata_landing")
    style = models.CharField(max_length=23, blank=True, null=True)
    dif_header = models.BooleanField(default=False, blank=False, null=False)
    dif_footer = models.BooleanField(default=False, blank=False, null=False)
    # file = models.FileField(upload_to="files", blank=True, null=True)
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # icon = models.ImageField(upload_to="ProductCategory/", blank=True, null=True)
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True,
                                 related_name="landing_set")

    class Meta:
        ordering = ['category', '-sort_number']
        verbose_name = "Landing"
        verbose_name_plural = "Landings"

    def __str__(self):
        return f"Landing: {self.title}"


class SectionType(models.TextChoices):
    BANNER = "بنر"
    TITLE = "عنوان"
    CATEGORY = "دسته بندی"
    INFO = "اطلاعات محصول"
    GALLERY = "گالری"
    VIDEO = "ویدیو"
    ARTICLE = "مقاله"
    QUESTION = "سوالات"
    PRICE_TABLE = "جدول قیمت"
    PARENT = "لندینگ مادر"
    FREE = "آزاد"


class Section(models.Model):
    section_type = models.CharField(max_length=23, choices=SectionType.choices, validators=[validators.MinLengthValidator(3)], verbose_name="section type",
                                    blank=False, null=False)
    section_order = models.IntegerField(default=0, blank=False, null=False, verbose_name="Section Order")
    landing = models.ForeignKey("Landing", on_delete=models.CASCADE, related_name="sections",
                                blank=False, null=False)
    elements = models.JSONField(default=dict, blank=False, null=False)

    class Meta:
        ordering = ['landing', '-section_order']
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return f"Section #{self.section_order}: {self.landing}"


class LandingCategoryType(models.TextChoices):
    PAGE = "صفحه ایستا"
    DOWNLOAD = "دانلود"
    ARTICLE = "مطلب"
    MAIN = "صفحه اصلی"
    CATEGORY = "محصولات"


class LandingCategory(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    parent_category = models.ForeignKey("LandingCategory", on_delete=models.PROTECT, blank=True, null=True, verbose_name="Parent Category",
                                        related_name="child_categories")
    description = models.TextField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")
    type = models.CharField(max_length=10, choices=LandingCategoryType.choices, default=LandingCategoryType.PAGE, validators=[validators.MinLengthValidator(4)],
                            blank=False, null=False)
    sort_number = models.IntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    metadata = models.OneToOneField(Metadata, on_delete=models.PROTECT, blank=False, null=False,
                                    related_name="metadata_category_landing")
    # image = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # icon = models.ImageField(upload_to="ProductCategory/", blank=True, null=True)
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False)

    class Meta:
        ordering = ['parent_category', '-sort_number']
        verbose_name = "Landing Category"
        verbose_name_plural = "Landing Categories"

    def __str__(self):
        return f"Landing Category: {self.title}"


class VisualMenuType(models.TextChoices):
    SLIDESHOW = "اسلاید شو"
    TIMER_GALLERY = "گالری زماندار"
    LANDING = "لندینگ"


class VisualMenu(models.Model):
    title = models.CharField(max_length=37, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    type = models.CharField(max_length=13, choices=VisualMenuType.choices, blank=False, null=False)
    # image1 = models.ImageField(upload_to="images/", blank=False, null=False)
    # image2 = models.ImageField(upload_to="images/", blank=False, null=False)
    # image3 = models.ImageField(upload_to="images/", blank=False, null=False)
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False)
    linked = models.BooleanField(default=False, blank=False, null=False)
    hyperlink = models.URLField(blank=True, null=True)
    landing = models.ForeignKey("Landing", on_delete=models.PROTECT, blank=True, null=True,
                                related_name="linked_visual_menu")
    sort_order = models.IntegerField(default=0, blank=False, null=False, verbose_name="Sort Order")
    fields = models.JSONField(default=dict, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")

    class Meta:
        ordering = ['-sort_order']
        verbose_name = "Visual Menu"
        verbose_name_plural = "Visual Menus"

    def __str__(self):
        return f"{self.type}: #{self.sort_order}-{self.title}"


class AlarmMassage(models.Model):
    title = models.CharField(max_length=37, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    content = models.TextField(max_length=300, blank=False, null=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True,
                                 related_name="alarm_massage_set")
    start_date = models.DateTimeField(blank=True, null=True, verbose_name="Start Date")
    end_date = models.DateTimeField(blank=False, null=False, verbose_name="End Date")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, blank=False, null=False,
                             related_name="alarm_massages")

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Alarm Massage"
        verbose_name_plural = "Alarms Massage"

    def __str__(self):
        return f"Alarm Massage: {self.title}"


class FileItem(models.Model):
    name = models.CharField(max_length=73, validators=[validators.MinLengthValidator(1)], blank=False, null=False)
    type = models.CharField(max_length=5, validators=[validators.MinLengthValidator(1)], blank=False, null=False)
    # preview = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # file = models.FileField(upload_to="uploads/", blank=False, null=False)
    date = models.DateField(default=timezone.now, blank=True, null=True, verbose_name="Start Date")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True,
                                 related_name="upload_files")
    volume = models.IntegerField(default=0, blank=False, null=False, verbose_name="Volume")
    directory = models.ForeignKey('FileDirectory', on_delete=models.PROTECT, blank=True, null=True,
                                  related_name="sub_files")

    class Meta:
        ordering = ['-date']
        verbose_name = "File Item"
        verbose_name_plural = "Files Item"

    def __str__(self):
        return f"File: {self.name}.{self.type}"


class FileDirectory(models.Model):
    name = models.CharField(max_length=73, validators=[validators.MinLengthValidator(1)], blank=False, null=False)
    date = models.DateField(default=timezone.now, blank=True, null=True, verbose_name="Start Date")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True,
                                 related_name="create_directory")
    volume = models.IntegerField(default=0, blank=False, null=False, verbose_name="Volume")
    parent = models.ForeignKey('FileDirectory', on_delete=models.PROTECT, blank=True, null=True,
                               related_name="sub_dirs")

    class Meta:
        ordering = ['-date']
        verbose_name = "File Directory"
        verbose_name_plural = "File Directories"

    def __str__(self):
        if self.parent:
            return f"{self.parent}/{self.name}/"
        else:
            return f"{self.name}/"
