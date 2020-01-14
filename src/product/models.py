from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.urls import reverse
from django.core import validators
import os


def classification_icon_directory_pass(instance, filename):
    return './product/static/img/classification/{0}/{1}-icon.png'.format(instance.id, instance.id)


def classification_preview_directory_pass(instance, filename):
    return './product/static/img/classification/{0}/{1}-preview.png'.format(instance.id, instance.id)


class Classification(models.Model):
    id = models.CharField(primary_key=True, max_length=3, validators=[validators.MinLengthValidator(3)])
    title = models.CharField(max_length=20, unique=True, blank=False, validators=[validators.MinLengthValidator(3)])
    icon = models.ImageField(upload_to=classification_icon_directory_pass, blank=False)
    preview = models.ImageField(upload_to=classification_preview_directory_pass, blank=True)
    description = models.TextField(max_length=2020, blank=True, validators=[validators.MinLengthValidator(3)])
    order = models.PositiveSmallIntegerField(default=0, unique=True)

    def __str__(self):
        return 'کلاس:‌ {0}'.format(self.title)


@receiver(models.signals.post_delete, sender=Classification)
def auto_delete_classification_img_on_delete(sender, instance, **kwargs):
    if instance.icon:
        if os.path.isfile(instance.icon.path):
            os.remove(instance.icon.path)
    if instance.preview:
        if os.path.isfile(instance.preview.path):
            os.remove(instance.preview.path)


@receiver(models.signals.pre_save, sender=Classification)
def auto_delete_classification_img_on_change(sender, instance, **kwargs):
    if not instance.id:
        return False
    try:
        old_icon = Classification.objects.get(pk=instance.id).icon
        old_preview = Classification.objects.get(pk=instance.id).preview
    except Classification.DoesNotExist:
        return False
    new_icon = instance.icon
    if not old_icon == new_icon and old_icon:
        if os.path.isfile(old_icon.path):
            os.remove(old_icon.path)
    new_preview = instance.preview
    if not old_preview == new_preview and old_preview:
        if os.path.isfile(old_preview.path):
            os.remove(old_preview.path)


def category_icon_directory_pass(instance, filename):
    return './product/static/img/category/{0}/{1}-icon.png'.format(instance.id, instance.id)


def category_preview_directory_pass(instance, filename):
    return './product/static/img/category/{0}/{1}-preview.png'.format(instance.id, instance.id)


class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=3, validators=[validators.MinLengthValidator(3)])
    title = models.CharField(max_length=20, default='جدید', blank=False, validators=[validators.MinLengthValidator(2)])
    icon = models.ImageField(upload_to=category_icon_directory_pass, blank=False)
    preview = models.ImageField(upload_to=category_preview_directory_pass, blank=True)
    classification = models.ForeignKey('Classification', on_delete=models.SET_NULL, null=True,
                                       related_name='all_category')
    description = models.TextField(max_length=2020, blank=True, validators=[validators.MinLengthValidator(3)])
    order = models.PositiveSmallIntegerField(default=0, unique=True)
    main = models.BooleanField(default=False)

    def __str__(self):
        return 'دسته: {0}'.format(self.title)

    def geturl(self):
        return reverse("product:category_show", kwargs={"category_id": self.id})

    def preview_url(self):
        return 'img/category/{0}/{1}-preview.png'.format(self.id, self.id)


@receiver(models.signals.post_delete, sender=Category)
def auto_delete_category_img_on_delete(sender, instance, **kwargs):
    if instance.icon:
        if os.path.isfile(instance.icon.path):
            os.remove(instance.icon.path)
    if instance.preview:
        if os.path.isfile(instance.preview.path):
            os.remove(instance.preview.path)


@receiver(models.signals.pre_save, sender=Category)
def auto_delete_category_img_on_change(sender, instance, **kwargs):
    if not instance.id:
        return False
    try:
        old_icon = Category.objects.get(pk=instance.id).icon
        old_preview = Category.objects.get(pk=instance.id).preview
    except Category.DoesNotExist:
        return False
    new_icon = instance.icon
    if not old_icon == new_icon and old_icon:
        if os.path.isfile(old_icon.path):
            os.remove(old_icon.path)
    new_preview = instance.preview
    if not old_preview == new_preview and old_preview:
        if os.path.isfile(old_preview.path):
            os.remove(old_preview.path)


def template_file_directory_path(instance, filename):
    return './product/static/file/template_file/{0}.zip'.format(instance.title)


# class Template_File_Format(models.TextChoices):
#     PHOTOSHOP = 'psd', 'PSD'
#     CORELDRAW = 'cdr', 'Corel'
#     ILLUSTRATOR = 'ai', 'ILLUSTRATOR'
#     PDF = 'pdf', 'PDF'


class TemplateFile(models.Model):
    title = models.CharField(max_length=50, blank=False, unique=True, validators=[validators.MinLengthValidator(3)])
    # template_file = models.FilePathField()
    tmp_file = models.FileField(upload_to=template_file_directory_path, blank=False)
    # format = models.CharField(max_length=3, blank=False,
    #                           choices=Template_File_Format.choices, default=Template_File_Format.PHOTOSHOP)
    # icon = models.ImageField(upload_to=template_file_icon_directory_path, blank=False)

    def __str__(self):
        return '{0}'.format(self.title)


@receiver(models.signals.post_delete, sender=TemplateFile)
def auto_delete_template_file_on_delete(sender, instance, **kwargs):
    if instance.tmp_file:
        if os.path.isfile(instance.tmp_file.path):
            os.remove(instance.tmp_file.path)


@receiver(models.signals.pre_save, sender=TemplateFile)
def auto_delete_template_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = TemplateFile.objects.get(pk=instance.pk).tmp_file
    except TemplateFile.DoesNotExist:
        return False
    new_file = instance.tmp_file
    if not old_file == new_file and old_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


def product_preview_directory_path(instance, filename):
    return './product/static/img/product/{0}/{1}-preview.png'.format(instance.id, instance.id)


def product_vector_directory_path(instance, filename):
    return './product/static/img/product/{0}/{1}-vector.png'.format(instance.id, instance.id)


class Product(models.Model):
    id = models.CharField(max_length=6, primary_key=True, validators=[validators.MinLengthValidator(6)])
    title = models.CharField(max_length=77, blank=False, validators=[validators.MinLengthValidator(3)])
    preview = models.ImageField(upload_to=product_preview_directory_path, blank=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True,
                                 related_name='all_product')
    # vector = models.ImageField(upload_to=product_vector_directory_path, blank=True)
    properties = models.TextField(max_length=2020, blank=True, validators=[validators.MinLengthValidator(100)])
    brief_intro = models.TextField(max_length=777, blank=True, validators=[validators.MinLengthValidator(10)])
    long_intro = models.TextField(max_length=5000, blank=True, validators=[validators.MinLengthValidator(10)])
    guidance = models.TextField(max_length=777, blank=True, validators=[validators.MinLengthValidator(30)])
    template_file = models.ForeignKey('TemplateFile', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='product_template')
    design_base = models.BooleanField(default=False)
    design_film = models.BooleanField(default=False)
    design_gold = models.BooleanField(default=False)
    design_form = models.BooleanField(default=False)
    services = models.ManyToManyField('Service', db_index=True, blank=False,
                                      related_name="all_service", through='ProductServices')

    # point
    # point result
    # comment
    # sales_option
    # brand
    # visit
    # sell
    # inventory
    # inventory_for_sale
    # gallery

    def __str__(self):
        return '{0}-{1}'.format(self.id, self.title)

    def geturl(self):
        return reverse("product:product_show", kwargs={"product_id": self.id})

    def preview_url(self):
        return 'img/product/{0}/{1}-preview.png'.format(self.id, self.id)

    def min_price(self):
        min_price = 0
        for tmp in self.selling_options.all():
            if min_price:
                if tmp.sale_price < min_price:
                    min_price = tmp.sale_price
            else:
                min_price = tmp.sale_price
        return min_price

    def min_ready(self):
        min_ready = 0
        for tmp in self.selling_options.all():
            if min_ready:
                if tmp.ready.duration < min_ready:
                    min_ready = tmp.ready.duration
            else:
                min_ready = tmp.ready.duration
        return min_ready

    def max_ready(self):
        max_ready = 0
        for tmp in self.selling_options.all():
            if max_ready:
                if tmp.ready.duration > max_ready:
                    max_ready = tmp.ready.duration
            else:
                max_ready = tmp.ready.duration
        return max_ready

    def file_number(self):
        num = 0
        if self.design_base:
            num += 1
        if self.design_film:
            num += 1
        if self.design_form:
            num += 1
        if self.design_gold:
            num += 1
        return num


@receiver(models.signals.post_delete, sender=Product)
def auto_delete_product_img_on_delete(sender, instance, **kwargs):
    if instance.preview:
        if os.path.isfile(instance.preview.path):
            os.remove(instance.preview.path)
    # if instance.vector:
    #     if os.path.isfile(instance.vector.path):
    #         os.remove(instance.vector.path)


@receiver(models.signals.pre_save, sender=Product)
def auto_delete_product_img_on_change(sender, instance, **kwargs):
    if not instance.id:
        return False
    try:
        old_preview = Product.objects.get(pk=instance.id).preview
        # old_vector = TemplateFile.objects.get(pk=instance.id).vector
    except Product.DoesNotExist:
        print('1')
        return False
    new_preview = instance.preview
    if not old_preview == new_preview and old_preview:
        if os.path.isfile(old_preview.path):
            print('2')
            os.remove(old_preview.path)
    # new_vector = instance.vector
    # if not old_vector == new_vector:
    #     if os.path.isfile(old_vector.path) and old_vector:
    #         os.remove(old_vector.path)


class Service(models.Model):
    title = models.CharField(max_length=30, blank=False, validators=[validators.MinLengthValidator(2)])
    cost = models.PositiveIntegerField(default=0, blank=False, validators=[validators.MinValueValidator(1000),
                                                                           validators.MaxValueValidator(1000000)])
    description = models.CharField(max_length=300, blank=True, validators=[validators.MinLengthValidator(3)])

    def __str__(self):
        return '{0}'.format(self.title)


class ProductServices(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                related_name="product_all_service")
    service = models.ForeignKey('Service', on_delete=models.CASCADE,
                                related_name="for_product")
    difference = models.IntegerField(default=0, blank=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '{0}-{1}'.format(self.service.title, self.product.title)


class OrderProductServices(models.Model):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE,
                              related_name="order_all_services")
    product_service = models.ForeignKey('ProductServices', on_delete=models.CASCADE,
                                        related_name="number_in_order")
    number = models.PositiveSmallIntegerField(default=1, blank=False, validators=[validators.MinValueValidator(1),
                                                                                  validators.MaxValueValidator(1000)])

    def __str__(self):
        return '{0}-{1}'.format(self.pk, self.product_service)


class Side(models.TextChoices):
    EMP = 0, 'غیر فعال'
    ONE = 1, 'یک رو'
    TWO = 2, 'دو رو'


class Size(models.Model):
    title = models.CharField(max_length=20, blank=False, validators=[validators.MinLengthValidator(2)])
    len = models.FloatField(blank=False, verbose_name='length', validators=[validators.MinValueValidator(2),
                                                                            validators.MaxValueValidator(100)])
    wid = models.FloatField(blank=False, verbose_name='width', validators=[validators.MinValueValidator(2),
                                                                           validators.MaxValueValidator(100)])
    cut_margin = models.FloatField(default=0, blank=False, validators=[validators.MinValueValidator(0),
                                                                       validators.MaxValueValidator(1)])
    safe_margin = models.FloatField(default=0, blank=False, validators=[validators.MinValueValidator(0),
                                                                        validators.MaxValueValidator(1)])
    description = models.CharField(max_length=50, blank=True, validators=[validators.MinLengthValidator(10)])

    def __str__(self):
        return '{0}'.format(self.title)

    class Meta:
        ordering = ['-len']


class Ready(models.Model):
    title = models.CharField(max_length=20, blank=False, validators=[validators.MinLengthValidator(3)])
    duration = models.PositiveSmallIntegerField(default=0, blank=False, validators=[validators.MaxValueValidator(30)])

    def __str__(self):
        return '{0}'.format(self.title)

    class Meta:
        ordering = ['-duration']


class Color(models.Model):
    title = models.CharField(max_length=20, blank=False, validators=[validators.MinLengthValidator(2)])
    code = models.CharField(max_length=7, default='#000000', validators=[validators.MinLengthValidator(7)])

    def __str__(self):
        return '{0}'.format(self.title)


class Quality(models.Model):
    title = models.CharField(max_length=20, blank=False, validators=[validators.MinLengthValidator(2)])

    def __str__(self):
        return '{0}'.format(self.title)


def design_preview_directory_path(instance, filename):
    return './product/static/img/design/{0}/{1}-preview.jpg'.format(instance.id, instance.id)


def design_vector_directory_path(instance, filename):
    return './product/static/img/design/{0}/{1}-vector.png'.format(instance.id, instance.id)


class Design(models.Model):
    id = models.CharField(max_length=3, primary_key=True, validators=[validators.MinLengthValidator(3)])
    title = models.CharField(max_length=20, blank=False, validators=[validators.MinLengthValidator(3)])
    preview = models.ImageField(upload_to=design_preview_directory_path, blank=False)
    vector = models.ImageField(upload_to=design_vector_directory_path, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=False,
                                 related_name='design_inf')
    price = models.PositiveIntegerField(default=0, blank=False, validators=[validators.MinValueValidator(10000),
                                                                            validators.MaxValueValidator(1000000)])
    # low_price = models.PositiveIntegerField(blank=True, validators=[validators.MinValueValidator(5000),
    #                                                                 validators.MaxValueValidator(500000)])
    max_time = models.PositiveSmallIntegerField(blank=False, validators=[validators.MinValueValidator(5),
                                                                         validators.MaxValueValidator(300)])
    duration = models.PositiveSmallIntegerField(blank=False, validators=[validators.MinValueValidator(0),
                                                                         validators.MaxValueValidator(30)])

    def __str__(self):
        return '{0}'.format(self.title)


@receiver(models.signals.post_delete, sender=Design)
def auto_delete_design_img_on_delete(sender, instance, **kwargs):
    if instance.preview:
        if os.path.isfile(instance.preview.path):
            os.remove(instance.preview.path)
    if instance.vector:
        if os.path.isfile(instance.vector.path):
            os.remove(instance.vector.path)


@receiver(models.signals.pre_save, sender=Design)
def auto_delete_design_img_on_change(sender, instance, **kwargs):
    if not instance.id:
        return False
    try:
        old_preview = TemplateFile.objects.get(pk=instance.id).preview
        old_vector = TemplateFile.objects.get(pk=instance.id).vector
    except TemplateFile.DoesNotExist:
        return False
    new_preview = instance.preview
    if not old_preview == new_preview and old_preview:
        if os.path.isfile(old_preview.path):
            os.remove(old_preview.path)
    new_vector = instance.vector
    if not old_vector == new_vector and old_vector:
        if os.path.isfile(old_vector.path):
            os.remove(old_vector.path)


class DiscountType(models.TextChoices):
    PERCENT = '%', 'درصدی'
    FIXED = '$', 'ثابت'


class Discount(models.Model):
    type = models.CharField(max_length=1, choices=DiscountType.choices, blank=False)
    amount = models.FloatField(blank=False, validators=[validators.MinValueValidator(0.1),
                                                        validators.MaxValueValidator(1000000)])
    title = models.CharField(max_length=15, blank=False, validators=[validators.MinLengthValidator(3)])

    def __str__(self):
        return '{0}'.format(self.type)


class SellingOption(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=False,
                                related_name='selling_options')
    side = models.CharField(max_length=1, choices=Side.choices, default=Side.EMP, blank=True)
    count = models.PositiveIntegerField(default=1000, blank=False, validators=[validators.MinValueValidator(1),
                                                                               validators.MaxValueValidator(100000)])
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
    base_price = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(1000),
                                                                      validators.MaxValueValidator(99999999)])
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='all_product')
    sale_price = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(1000),
                                                                      validators.MaxValueValidator(99999999)])

    def __str__(self):
        return '{0}'.format(self.product)

    class Meta:
        ordering = ['size', 'ready', 'count', '-side', ]

