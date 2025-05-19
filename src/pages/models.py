from django.db import models
from django.core import validators


class SectionType(models.TextChoices):
    BANNER = "بنر"
    TITLE = "عنوان"
    CATEGORY = "دسته بندی"
    INFO = "اطلاعات"
    GALLERY = "گالری"
    ARTICLE = "مقاله"
    QUESTION = "سوالات"
    PRICE_TABLE = "جدول قیمت"
    PARENT = "لندینگ مادر"
    FREE = "آزاد"


class PageSize(models.TextChoices):
    DEFAULT = "پیشفرض"
    FULL = "تمام صفحه"


class Metadata(models.Model):
    seo_title = models.CharField(max_length=100, unique=True, validators=[validators.MinLengthValidator(10)],
                                 blank=False, null=False)
    seo_description = models.TextField(max_length=300, validators=[validators.MinLengthValidator(10)], blank=True, null=True)
    seo_slug = models.SlugField(max_length=100, unique=True, blank=False, null=False)
    canonical_link = models.URLField(blank=True, null=True)
    keywords = models.TextField(max_length=300, blank=True, null=True)
    no_index = models.BooleanField(default=False, blank=False, null=False)
    no_index_child = models.BooleanField(default=False, blank=False, null=False)
    # اگر دسته زیر مجموعه هر قسمتی از متا دیتاش خالی بود از اولین دسته بالاتر پر بشه
    parent_metadata = models.BooleanField(default=False, blank=False, null=False)
    redirect_303 = models.BooleanField(default=False, blank=False, null=False)
    redirect_303_link = models.URLField(blank=True, null=True)


class Landing(models.Model):
    page_size = models.CharField(max_length=10, choices=PageSize.choices, default=PageSize.DEFAULT,
                                 blank=False, null=False)


class Section(models.Model):
    section_type = models.CharField(max_length=23, choices=SectionType.choices, validators=[validators.MinLengthValidator(3)],
                                    blank=False, null=False)
    section_order = models.IntegerField(default=0, blank=False, null=False)
    landing = models.ForeignKey("Landing", on_delete=models.CASCADE, related_name="sections",
                                blank=False, null=False)
    elements = models.JSONField(default=dict, blank=False, null=False)
