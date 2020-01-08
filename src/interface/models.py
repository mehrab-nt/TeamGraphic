from django.db import models
from django.core import validators


class MainMenu(models.Model):
    title = models.CharField(max_length=20, validators=[validators.MinLengthValidator(3)])
    link = models.CharField(max_length=20, validators=[validators.MinLengthValidator(2)])
    rank = models.PositiveSmallIntegerField(unique=True, blank=False, validators=[validators.MinValueValidator(1),
                                                                                  validators.MaxValueValidator(20)])
    active = models.BooleanField(default=True)
# محصولات
# تعرفه قیمت چاپ
# درباره ما
# بلاگ
# ارتباط با ما
# دعوت به همکاری


def background_image_directory_path(instance, filename):
    return './interface/static/img/main/background-{0}.jpg'.format(instance.title)


def header_image_directory_path(instance, filename):
    return './interface/static/img/main/header-{0}.jpg'.format(instance.title)


class MainImage(models.Model):
    title = models.CharField(max_length=20, validators=[validators.MinLengthValidator(3)])
    background = models.ImageField(upload_to=background_image_directory_path)
    header = models.ImageField(upload_to=header_image_directory_path)


def slide_show_directory_path(instance, filename):
    return './interface/static/img/slideshow/{0}.jpg'.format(instance.rank)


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
        return 'img/slideshow/{0}.jpg'.format(self.rank)

    def get_absolute_url(self):
        return '{0}'.format(self.link)
# id / img / time / order / link


class SpecialProductBox(models.Model):
    rank = models.PositiveSmallIntegerField(blank=False, unique=True, validators=[validators.MinValueValidator(1),
                                                                                  validators.MaxValueValidator(1000)])
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, blank=False)
# id / title / product_id (foreign_key)  / order


# product_show
# id / description / img_size / link (کارت ویزیت)

