from django.db import models
from django.utils import timezone


class Classification(models.Model):
    id = models.CharField(primary_key=True, max_length=3)
    title = models.CharField(max_length=20, blank=False)
    icon = models.ImageField(blank=False)
    preview = models.ImageField(blank=True)
    description = models.TextField(max_length=2020, blank=True)
    order = models.PositiveSmallIntegerField(default=0)


class Category(models.Model):
    title = models.CharField(max_length=20, default='جدید', blank=False)
    icon = models.ImageField()
    preview = models.ImageField(blank=True)
    classification = models.ForeignKey('Classification', on_delete=models.SET_NULL, null=True)
    description = models.TextField(max_length=2020, blank=True)
    order = models.PositiveSmallIntegerField(default=0)


def template_file_directory_path(instance, filename):
    return './product/template_file/{0}_{1}'.format(instance, filename)


class Template_File(models.Model):
    title = models.CharField(max_length=25, blank=False)
    # template_file = models.FilePathField()
    tmp_file = models.FileField(upload_to=template_file_directory_path, blank=False)


class Product(models.Model):
    title = models.CharField(max_length=77, blank=False)
    preview = models.ImageField(blank=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    vector = models.ImageField(upload_to='.', blank=True)
    properties = models.TextField(max_length=2020, blank=True)
    brief_intro = models.TextField(max_length=777, blank=True)
    long_intro = models.TextField(max_length=5000, blank=True)
    guidance = models.TextField(max_length=777, blank=True)
    template_file = models.ForeignKey('Template_File', on_delete=models.SET_NULL, null=True, blank=True)
    design_feature = models.BooleanField(blank=False)
    # point
    # point result
    # comment
    # sales_option
    # brand
    # visit
    # sell
    # inventory
    # inventory_for_sale


class Side(models.TextChoices):
    EMP = 0, 'غیر فعال'
    ONE = 1, 'یک رو'
    TWO = 2, 'دو رو'


class Cut(models.Model):
    title = models.CharField(max_length=10, blank=False)
    cut_margin = models.FloatField(blank=False)
    safe_margin = models.FloatField(blank=False)
    # vector


class Size(models.Model):
    title = models.CharField(max_length=20, blank=False)
    len = models.FloatField(blank=False, verbose_name='length')
    wid = models.FloatField(blank=False, verbose_name='width')
    description = models.CharField(max_length=50, blank=True)


class Ready(models.Model):
    title = models.CharField(max_length=20, blank=False)
    duration = models.PositiveSmallIntegerField(default=0, blank=False)


class Color(models.Model):
    title = models.CharField(max_length=20, blank=False)
    code = models.CharField(max_length=7, default='#000000')


class Quality(models.Model):
    title = models.CharField(max_length=20, blank=False)


class Design(models.Model):
    title = models.CharField(max_length=20, blank=False)
    preview = models.ImageField(blank=False)
    vector = models.ImageField(blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=False,
                                 related_name='design_inf')
    price = models.PositiveIntegerField(default=0, blank=False)
    low_price = models.PositiveIntegerField(blank=True)
    min_time = models.PositiveSmallIntegerField(blank=False)
    duration = models.PositiveSmallIntegerField(blank=False)


class Discount_Type(models.TextChoices):
    PERCENT = '%', 'درصدی'
    FIXED = '$', 'ثابت'


class Discount(models.Model):
    type = models.CharField(max_length=1, choices=Discount_Type.choices, blank=False)
    amount = models.PositiveIntegerField(blank=False)
    title = models.CharField(max_length=15, blank=False)


class Selling_Option(models.Model):
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=False,
                                related_name='selling_options')
    side = models.CharField(max_length=1, choices=Side.choices, default=Side.EMP, blank=True)
    count = models.PositiveIntegerField(default=1000, blank=False)
    size = models.ForeignKey('Size', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='all_product')
    ready = models.ForeignKey('Ready', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='all_product')
    color = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='product_body')
    ink = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='product_ink')
    # line_up
    lat = models.BooleanField(default=False)
    # sheet = models.PositiveSmallIntegerField(blank=False)
    # cover # for catalog
    # color_mode
    quality = models.ForeignKey('Quality', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='all_product')
    base_price = models.PositiveIntegerField(blank=False)
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='all_product')
    sale_price = models.PositiveIntegerField(blank=False)

