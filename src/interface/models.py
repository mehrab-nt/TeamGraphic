from django.db import models
from django.core import validators
from django.dispatch import receiver
import os


class MainMenu(models.Model):
    title = models.CharField(max_length=20, validators=[validators.MinLengthValidator(3)])
    link = models.CharField(max_length=20, validators=[validators.MinLengthValidator(2)])
    rank = models.PositiveSmallIntegerField(unique=True, blank=False, validators=[validators.MinValueValidator(1),
                                                                                  validators.MaxValueValidator(20)])
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'منو اصلی'
        verbose_name_plural = 'منو اصلی'
# محصولات
# تعرفه قیمت چاپ
# درباره ما
# بلاگ
# ارتباط با ما
# دعوت به همکاری


def background_image_directory_path(instance, filename):
    return './interface/static/img/main/background-{0}.png'.format(instance.title)


def header_image_directory_path(instance, filename):
    return './interface/static/img/main/header-{0}.png'.format(instance.title)


class MainImage(models.Model):
    title = models.CharField(max_length=20, validators=[validators.MinLengthValidator(3)])
    background = models.ImageField(upload_to=background_image_directory_path)
    header = models.ImageField(upload_to=header_image_directory_path)

    class Meta:
        verbose_name = 'عکس های اصلی'
        verbose_name_plural = 'عکس های اصلی'


def slide_show_directory_path(instance, filename):
    return './interface/static/img/slideshow/{0}.png'.format(instance.rank)


class SlideShow(models.Model):
    title = models.CharField(max_length=20, validators=[validators.MinLengthValidator(3)], unique=True)
    image = models.ImageField(upload_to=slide_show_directory_path)
    rank = models.PositiveSmallIntegerField(blank=False, unique=True, validators=[validators.MinValueValidator(1),
                                                                                  validators.MaxValueValidator(100)])
    link = models.CharField(max_length=20, validators=[validators.MinLengthValidator(1)], default='/')
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=50, blank=True)
    time = models.FloatField(blank=False, validators=[validators.MinValueValidator(1),
                                                      validators.MaxValueValidator(10)])

    def get_image_url(self):
        return 'img/slideshow/{0}.png'.format(self.rank)

    def get_absolute_url(self):
        return '{0}'.format(self.link)

    class Meta:
        verbose_name = 'اسلاید شو'
        verbose_name_plural = 'اسلاید شو'
# id / img / time / order / link


@receiver(models.signals.post_delete, sender=SlideShow)
def auto_delete_slide_show_img_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=SlideShow)
def auto_delete_slide_show_img_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_image = SlideShow.objects.get(pk=instance.pk).image
    except SlideShow.DoesNotExist:
        return False
    new_image = instance.image
    if not old_image == new_image and old_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)


class SpecialProductBox(models.Model):
    rank = models.PositiveSmallIntegerField(blank=False, unique=True, validators=[validators.MinValueValidator(1),
                                                                                  validators.MaxValueValidator(1000)])
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, blank=False)

    class Meta:
        verbose_name = 'محصولات خاص'
        verbose_name_plural = 'محصولات خاص'
# id / title / product_id (foreign_key)  / order


# product_show
# id / description / img_size / link (کارت ویزیت)

