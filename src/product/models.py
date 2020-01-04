from django.db import models
from django.utils import timezone
from django.dispatch import receiver
import os


def classification_icon_directory_pass(instance, filename):
    return './product/static/img/classification/{0}/{1}-icon.png'.format(instance.id, instance.id)


def classification_preview_directory_pass(instance, filename):
    return './product/static/img/classification/{0}/{1}-preview.jpg'.format(instance.id, instance.id)


class Classification(models.Model):
    id = models.CharField(primary_key=True, max_length=3)
    title = models.CharField(max_length=20, blank=False)
    icon = models.ImageField(upload_to=classification_icon_directory_pass, blank=False)
    preview = models.ImageField(upload_to=classification_preview_directory_pass, blank=True)
    description = models.TextField(max_length=2020, blank=True)
    order = models.PositiveSmallIntegerField(default=0)


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
    if not old_icon == new_icon:
        if os.path.isfile(old_icon.path):
            os.remove(old_icon.path)
    new_preview = instance.preview
    if not old_preview == new_preview:
        if os.path.isfile(old_preview.path):
            os.remove(old_preview.path)


def category_icon_directory_pass(instance, filename):
    return './product/static/img/category/{0}/{1}-icon.png'.format(instance.id, instance.id)


def category_preview_directory_pass(instance, filename):
    return './product/static/img/category/{0}/{1}-preview.jpg'.format(instance.id, instance.id)


class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=3)
    title = models.CharField(max_length=20, default='جدید', blank=False)
    icon = models.ImageField(upload_to=category_icon_directory_pass, blank=False)
    preview = models.ImageField(upload_to=category_preview_directory_pass, blank=True)
    classification = models.ForeignKey('Classification', on_delete=models.SET_NULL, null=True)
    description = models.TextField(max_length=2020, blank=True)
    order = models.PositiveSmallIntegerField(default=0)


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
    if not old_icon == new_icon:
        if os.path.isfile(old_icon.path):
            os.remove(old_icon.path)
    new_preview = instance.preview
    if not old_preview == new_preview:
        if os.path.isfile(old_preview.path):
            os.remove(old_preview.path)


def template_file_directory_path(instance, filename):
    return './product/static/file/template_file/{0}.zip'.format(instance.title)


# class Template_File_Format(models.TextChoices):
#     PHOTOSHOP = 'psd', 'PSD'
#     CORELDRAW = 'cdr', 'Corel'
#     ILLUSTRATOR = 'ai', 'ILLUSTRATOR'
#     PDF = 'pdf', 'PDF'


class Template_File(models.Model):
    title = models.CharField(max_length=50, blank=False, unique=True)
    # template_file = models.FilePathField()
    tmp_file = models.FileField(upload_to=template_file_directory_path, blank=False)
    # format = models.CharField(max_length=3, blank=False,
    #                           choices=Template_File_Format.choices, default=Template_File_Format.PHOTOSHOP)
    # icon = models.ImageField(upload_to=template_file_icon_directory_path, blank=False)


@receiver(models.signals.post_delete, sender=Template_File)
def auto_delete_template_file_on_delete(sender, instance, **kwargs):
    if instance.tmp_file:
        if os.path.isfile(instance.tmp_file.path):
            os.remove(instance.tmp_file.path)


@receiver(models.signals.pre_save, sender=Template_File)
def auto_delete_template_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = Template_File.objects.get(pk=instance.pk).tmp_file
    except Template_File.DoesNotExist:
        return False
    new_file = instance.tmp_file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


def product_preview_directory_path(instance, filename):
    return './product/static/img/product/{0}/{1}-preview.jpg'.format(instance.id, instance.id)


def product_vector_directory_path(instance, filename):
    return './product/static/img/product/{0}/{1}-vector.png'.format(instance.id, instance.id)


class Product(models.Model):
    id = models.CharField(max_length=6, primary_key=True)
    title = models.CharField(max_length=77, blank=False)
    preview = models.ImageField(upload_to=product_preview_directory_path, blank=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    # vector = models.ImageField(upload_to=product_vector_directory_path, blank=True)
    properties = models.TextField(max_length=2020, blank=True)
    brief_intro = models.TextField(max_length=777, blank=True)
    long_intro = models.TextField(max_length=5000, blank=True)
    guidance = models.TextField(max_length=777, blank=True)
    template_file = models.ForeignKey('Template_File', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='product_template')
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
    # gallery


@receiver(models.signals.post_delete, sender=Product)
def auto_delete_product_img_on_delete(sender, instance, **kwargs):
    if instance.preview:
        if os.path.isfile(instance.preview.path):
            os.remove(instance.preview.path)
    if instance.vector:
        if os.path.isfile(instance.vector.path):
            os.remove(instance.vector.path)


@receiver(models.signals.pre_save, sender=Product)
def auto_delete_product_img_on_change(sender, instance, **kwargs):
    if not instance.id:
        return False
    try:
        old_preview = Template_File.objects.get(pk=instance.id).preview
        old_vector = Template_File.objects.get(pk=instance.id).vector
    except Template_File.DoesNotExist:
        return False
    new_preview = instance.preview
    if not old_preview == new_preview:
        if os.path.isfile(old_preview.path):
            os.remove(old_preview.path)
    new_vector = instance.vector
    if not old_vector == new_vector:
        if os.path.isfile(old_vector.path):
            os.remove(old_vector.path)


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


def design_preview_directory_path(instance, filename):
    return './product/static/img/design/{0}/{1}-preview.jpg'.format(instance.id, instance.id)


def design_vector_directory_path(instance, filename):
    return './product/static/img/design/{0}/{1}-vector.png'.format(instance.id, instance.id)


class Design(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    title = models.CharField(max_length=20, blank=False)
    preview = models.ImageField(upload_to=design_preview_directory_path, blank=False)
    vector = models.ImageField(upload_to=design_vector_directory_path, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=False,
                                 related_name='design_inf')
    price = models.PositiveIntegerField(default=0, blank=False)
    low_price = models.PositiveIntegerField(blank=True)
    min_time = models.PositiveSmallIntegerField(blank=False)
    duration = models.PositiveSmallIntegerField(blank=False)


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
        old_preview = Template_File.objects.get(pk=instance.id).preview
        old_vector = Template_File.objects.get(pk=instance.id).vector
    except Template_File.DoesNotExist:
        return False
    new_preview = instance.preview
    if not old_preview == new_preview:
        if os.path.isfile(old_preview.path):
            os.remove(old_preview.path)
    new_vector = instance.vector
    if not old_vector == new_vector:
        if os.path.isfile(old_vector.path):
            os.remove(old_vector.path)


class Discount_Type(models.TextChoices):
    PERCENT = '%', 'درصدی'
    FIXED = '$', 'ثابت'


class Discount(models.Model):
    type = models.CharField(max_length=1, choices=Discount_Type.choices, blank=False)
    amount = models.PositiveIntegerField(blank=False)
    title = models.CharField(max_length=15, blank=False)


class Selling_Option(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=False,
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

