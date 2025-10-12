from django.db import models
from django.core import validators


class ApiCategory(models.Model):
    title = models.CharField(max_length=37, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    sort_number = models.IntegerField(default=0,
                                      blank=False, null=False, verbose_name='Sort Number')
    role_base = models.BooleanField(default=False, blank=False, null=False,
                                    verbose_name='Role Base')

    class Meta:
        ordering = ['role_base', 'sort_number']
        verbose_name = 'API Category'
        verbose_name_plural = 'API Categories'

    def __str__(self):
        return f'Api Category: {self.title}'


class ApiItem(models.Model):
    title = models.CharField(max_length=37, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    sort_number = models.IntegerField(default=0,
                                      blank=False, null=False, verbose_name='Sort Number')
    key = models.CharField(max_length=37, unique=True, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False, db_index=True)
    category = models.ForeignKey(ApiCategory, on_delete=models.PROTECT, blank=False, null=False,
                                 related_name='api_items')

    class Meta:
        ordering = [ 'category', 'sort_number',]
        verbose_name = 'API Item'
        verbose_name_plural = 'API Items'

    def __str__(self):
        return f'{self.key}'
