from django.db import models
from django.core import validators
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
from employee.models import Employee
from .images import *
from django.core.exceptions import ValidationError


class FileDirectory(MPTTModel):
    name = models.CharField(max_length=78, validators=[validators.MinLengthValidator(1)],
                            blank=False, null=False)
    create_date = models.DateField(auto_now_add=True,
                                   blank=True, null=True, verbose_name='Create Date')
    parent_directory = TreeForeignKey('self', on_delete=models.CASCADE,
                                      blank=True, null=True, verbose_name='Parent Directory',
                                      related_name='sub_dirs')

    class Meta:
        ordering = ['-create_date']
        verbose_name = "File Directory"
        verbose_name_plural = "File Directories"

    class MPTTMeta:
        order_insertion_by = ['create_date', 'name']
        parent_attr = 'parent_directory'

    def __str__(self):
        return '/'.join([ancestor.name for ancestor in self.get_ancestors(include_self=True)]) + '/'

    def clean(self): # MEH: Prevent circular reference A → B → C → A in Admin Panel
        if self.parent_directory:
            if self == self.parent_directory:
                raise ValidationError("A directory cannot be its own parent.")
            if self.pk and self.parent_directory.is_descendant_of(self):
                raise ValidationError("You cannot assign a descendant as the parent directory.")

def upload_path(instance): # MEH: Tree based Directory handle (and safe slug for names)
    directory = instance.parent_directory
    path_parts = []
    while directory:
        path_parts.insert(0, safe_slug(directory.name))
        directory = directory.parent_directory
    path = '/'.join(path_parts)
    return path

def get_random_basename(instance): # MEH: With this image and thumbnail get equal name
    if not hasattr(instance, "_random_basename"):
        instance._random_basename = uuid.uuid4().hex[:8]
    return instance._random_basename

def preview_image_path(instance, filename): # MEH: Create a dir for thumbnail in each folder
    path = upload_path(instance)
    base_name = get_random_basename(instance)
    filename = f"thumb-{base_name}.webp"
    return f'file_manager/{path}/thumbnails/{filename}'

def upload_file_path(instance, filename): # MEH: Upload File here (with safe slug name)
    path = upload_path(instance)
    base_name = get_random_basename(instance)
    filename = f"{base_name}.{instance.type}"
    return f'file_manager/{path}/{filename}'


class FileItem(models.Model):
    name = models.CharField(max_length=78, validators=[validators.MinLengthValidator(1)],
                            blank=True, null=False)
    type = models.CharField(max_length=5, validators=[validators.MinLengthValidator(1)],
                            blank=True, null=False)
    preview = models.ImageField(upload_to=preview_image_path, blank=True, null=True)
    file = models.FileField(upload_to=upload_file_path, blank=False, null=False)
    create_date = models.DateField(auto_now_add=True,
                                   blank=True, null=True, verbose_name='Create Date')
    volume = models.FloatField(default=0,
                               blank=False, null=False)
    parent_directory = models.ForeignKey(FileDirectory, on_delete=models.CASCADE,
                                         blank=True, null=True, verbose_name='Parent Directory',
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
            name, ext = os.path.splitext(filename)
            if not self.name:
                self.name = name
            self.type = ext.lstrip('.')
            self.volume = self.file.size / 1024 # MEH: KB
        if self.file and not self.preview and self.type.lower() in ['jpg', 'jpeg', 'png', 'webp']:
            self.preview = create_square_thumbnail(self.file, size=(128, 128))
        super().save(*args, **kwargs)

    @property
    def full_file_name(self):
        return f'{self.name}.{self.type}'

    def get_download_url(self):
        return self.file.url


class ClearFileHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=False, null=False,
                                 related_name='clear_file_actions')
    from_date = models.DateField(blank=False, null=False, verbose_name='From Date')
    until_date = models.DateField(blank=False, null=False, verbose_name='Last Update')
    submit_date = models.DateTimeField(auto_now_add=True,
                                       verbose_name='Submit Date')
    delete_number = models.PositiveIntegerField(default=0,
                                                blank=False, null=False, verbose_name='Delete Number')

    class Meta:
        ordering = ['-submit_date']
        verbose_name = "Clear File History"
        verbose_name_plural = "Clear File Histories"

    def clear_order_files(self): # MEH: Delete old file in request range if The File in an Order (for delete Other Files di it manually)
        qs_file = FileItem.objects.filter(create_date__range=[self.from_date, self.until_date], for_orders__isnull=False).distinct()
        deleted_count, _ = qs_file.delete()
        self.delete_number = deleted_count
        self.save(update_fields=['delete_number'])
        return deleted_count
