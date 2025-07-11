from django.db import models
from django.core import validators
from django.utils import timezone
from employee.models import Employee
from .images import *
from django.core.exceptions import ValidationError
from api.responses import TG_PREVENT_CIRCULAR_CATEGORY


class FileDirectory(models.Model):
    name = models.CharField(max_length=78, validators=[validators.MinLengthValidator(1)],
                            blank=False, null=False)
    create_date = models.DateField(default=timezone.now,
                                   blank=True, null=True, verbose_name='Create Date')
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
            return f"{self.name}"

    def clean(self): # MEH: Prevent circular reference A → B → C → A in Admin Panel
        current = self.parent_directory
        while current:
            if current == self:
                raise ValidationError(TG_PREVENT_CIRCULAR_CATEGORY)
            current = current.parent_directory

    def delete_recursive(self):
        for sub_dir in self.sub_dirs.all(): # MEH: First delete subdirectories recursively
            sub_dir.delete_recursive()
        self.sub_files.all().delete() # MEH: Delete files in this directory
        self.delete() # MEH: Then delete the directory itself


def upload_path(instance): # MEH: Tree based Directory handle (and safe slug for names)
    directory = instance.parent_directory
    path_parts = []
    while directory:
        path_parts.insert(0, safe_slug(directory.name))
        directory = directory.parent_directory
    path = '/'.join(path_parts)
    return path

def preview_image_path(instance, filename): # MEH: Create a dir for thumbnail in each folder
    path = upload_path(instance)
    filename = f"thumb-{safe_slug(instance.name)}.webp"
    return f'file_manager/{path}/thumbnails/{filename}'

def upload_file_path(instance, filename): # MEH: Upload File here (with safe slug name)
    path = upload_path(instance)
    filename = f"{safe_slug(instance.name)}.{instance.type}"
    return f'file_manager/{path}/{filename}'


class FileItem(models.Model):
    name = models.CharField(max_length=78, validators=[validators.MinLengthValidator(1)],
                            blank=True, null=False)
    type = models.CharField(max_length=5, validators=[validators.MinLengthValidator(1)],
                            blank=True, null=False)
    preview = models.ImageField(upload_to=preview_image_path, blank=True, null=True)
    file = models.FileField(upload_to=upload_file_path, blank=False, null=False)
    create_date = models.DateField(default=timezone.now,
                                   blank=True, null=True, verbose_name='Create Date')
    volume = models.FloatField(default=0,
                               blank=False, null=False)
    parent_directory = models.ForeignKey(FileDirectory, on_delete=models.PROTECT, blank=True, null=True,
                                  related_name='sub_files')
    seo_base = models.BooleanField(default=False,
                                   blank=False, null=False, verbose_name='SEO Base')

    class Meta:
        ordering = ['-create_date']
        verbose_name = "File Item"
        verbose_name_plural = "File Items"

    def __str__(self):
        return f"File: {self.name}.{self.type}"

    def save(self, *args, **kwargs):
        if self.file: # MEH: Set attr first time File save in system
            filename = self.file.name.split('/')[-1]
            self.name, ext = os.path.splitext(filename)
            self.type = ext.lstrip('.')
            self.volume = self.file.size / 1024 # MEH: KB
        if self.file and not self.preview and self.type.lower() in ['jpg', 'jpeg', 'png', 'webp']:
            self.preview = create_square_thumbnail(self.file, size=(128, 128))
        super().save(*args, **kwargs)

    @property
    def full_filename(self):
        return f'{self.name}.{self.type}'

    def get_download_url(self):
        return self.file.url
