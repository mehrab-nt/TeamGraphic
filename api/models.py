from django.db import models
from django.core import validators


class ApiCategory(models.Model):
    title = models.CharField(max_length=37, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    sort_number = models.IntegerField(default=0,
                                      blank=False, null=False, verbose_name='Sort Number')

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "API Category"
        verbose_name_plural = "API Categories"

    def __str__(self):
        return f'Api Category: {self.title}'


class ApiItem(models.Model):
    title = models.CharField(max_length=37, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    sort_number = models.IntegerField(default=0,
                                      blank=False, null=False, verbose_name='Sort Number')
    key = models.CharField(max_length=37, unique=True, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False)

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "API Item"
        verbose_name_plural = "API Items"

    def __str__(self):
        return f'Api Item: {self.title} #{self.key}'
