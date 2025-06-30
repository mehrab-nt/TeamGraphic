from django.db import models


class Province(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    tel_prefix = models.CharField(max_length=10)

    class Meta:
        db_table = 'provinces'
        verbose_name_plural = 'provinces'
        ordering = ['name']

    def __str__(self):
        return self.name


class City(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    province = models.ForeignKey('Province', on_delete=models.PROTECT,
                                 related_name='cities')

    class Meta:
        db_table = 'cities'
        verbose_name_plural = 'cities'
        ordering = ['province', 'name']
        unique_together = ('name', 'province')

    def __str__(self):
        return self.name
