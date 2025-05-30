from django.db import models
from django.core import validators
from django.utils import timezone
from employee.models import Employee


class FileDirectory(models.Model):
    name = models.CharField(max_length=78, validators=[validators.MinLengthValidator(1)],
                            blank=False, null=False)
    create_date = models.DateField(default=timezone.now,
                                   blank=True, null=True, verbose_name='Create Date')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True,
                                 related_name='create_directory_list')
    volume = models.IntegerField(default=0,
                                 blank=False, null=False)
    parent_directory = models.ForeignKey('self', on_delete=models.PROTECT,
                               blank=True, null=True, verbose_name='Parent Directory',
                               related_name='sub_dirs')

    class Meta:
        ordering = ['-create_date']
        verbose_name = "File Directory"
        verbose_name_plural = "File Directories"

    def __str__(self):
        if self.parent_directory:
            return f"{self.parent_directory}/{self.name}/"
        else:
            return f"{self.name}/"


class FileItem(models.Model):
    name = models.CharField(max_length=78, validators=[validators.MinLengthValidator(1)],
                            blank=False, null=False)
    type = models.CharField(max_length=5, validators=[validators.MinLengthValidator(1)],
                            blank=False, null=False)
    # preview = models.ImageField(upload_to="ProductCategory/", blank=False, null=False)
    # file = models.FileField(upload_to="uploads/", blank=False, null=False)
    upload_date = models.DateField(default=timezone.now,
                                   blank=True, null=True, verbose_name='Upload Date')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='upload_file_list')
    volume = models.IntegerField(default=0,
                                 blank=False, null=False)
    directory = models.ForeignKey(FileDirectory, on_delete=models.PROTECT, blank=True, null=True,
                                  related_name='sub_files')

    class Meta:
        ordering = ['-upload_date', 'directory']
        verbose_name = "File Item"
        verbose_name_plural = "File Items"

    def __str__(self):
        return f"File: {self.name}.{self.type}"
