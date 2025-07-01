from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.utils import timezone
from django.core.exceptions import ValidationError
from city.models import City, Province
from api.responses import *
import string, random


class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True, validators=[validators.MinLengthValidator(11)],
                                    blank=False, null=False, verbose_name='Phone Number')
    national_id = models.CharField(max_length=10, unique=True, default=None, validators=[validators.MinLengthValidator(10)],
                                   blank=True, null=True, verbose_name='National ID')
    public_key = models.CharField(max_length=8, unique=True, validators=[validators.MinLengthValidator(8)],
                                  blank=True, null=False, verbose_name='Public Key')
    private_key = models.CharField(max_length=16, unique=True,
                                   blank=True, null=False, verbose_name='Private Key')
    accounting_id = models.PositiveBigIntegerField(unique=True,
                                                   blank=True, null=True, verbose_name='Accounting ID')
    accounting_name = models.CharField(max_length=73, blank=True, null=True, verbose_name='Accounting Name')
    role = models.ForeignKey('Role', on_delete=models.SET_NULL,
                             blank=False, null=True,
                             related_name='role_all_users')
    is_employee = models.BooleanField(default=False, db_index=True,
                                      blank=False, null=False, verbose_name='Is Employee')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f'#{self.pk}: {self.first_name} {self.last_name} ({self.phone_number})'

    def set_user_activation(self, activate=False):
        self.is_active = activate
        self.save()

    @staticmethod
    def generate_unique_key(self, field_name, length, prefix=''):
        chars = string.ascii_lowercase + string.digits
        while True:
            prefix += ''.join(random.choices(chars, k=length-len(prefix)))
            if not self.objects.filter(**{field_name: prefix}).exists():
                return prefix

    def save(self, *args, **kwargs):
        if not self.public_key or 'tg-' not in self.public_key:
            self.public_key = self.generate_unique_key(User,'public_key', 8, 'tg-')
        if not self.private_key or len(self.private_key) != 16:
            self.private_key = self.generate_unique_key(User, 'private_key', 16)
        if not self.phone_number:
            self.phone_number = self.username
        if not self.role:
            self.role = Role.objects.filter(is_default=True).first()
        super().save(*args, **kwargs)


class GENDER(models.TextChoices):
    MALE = 'M', 'مرد'
    FEMALE = 'F', 'زن'
    UNDEFINED = 'U', 'تعیین نشده'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='user_profile')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Birth Date')
    gender = models.CharField(max_length=1, choices=GENDER.choices, default=GENDER.UNDEFINED, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    introduce_from = models.ForeignKey('Introduction', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Introduction from',
                                       related_name='introduce_all_users')
    job = models.CharField(max_length=23, blank=True, null=True,
                           db_index=True)

    class Meta:
        ordering = ['user']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile: {self.user}"


class Role(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=236, blank=True, null=True)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name='Sort Number')
    is_default = models.BooleanField(default=False, blank=False, null=False, verbose_name='Is Default')

    class Meta:
        ordering = ['sort_number']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return f'Role: {self.title}'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            other_default = Role.objects.exclude(pk=self.pk).filter(is_default=True)
            if self.is_default:
                if other_default.exists():
                    other_default.update(is_default=False)
            else:
                if not other_default.exists():
                    self.is_default = True
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_default:
            raise ValidationError(TG_PREVENT_DELETE_DEFAULT)
        super().delete(*args, **kwargs)


class Introduction(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    number = models.PositiveIntegerField(default=0, blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name='Sort Number')

    class Meta:
        ordering = ['sort_number']
        verbose_name = 'Introduce'
        verbose_name_plural = 'Introduces'

    def __str__(self):
        return self.title


class Address(models.Model):
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             blank=False, null=False,
                             related_name='user_addresses')
    # todo: location GIS
    province = models.ForeignKey(Province, on_delete=models.PROTECT,
                                 blank=False, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT,
                             blank=True, null=True)
    content = models.TextField(max_length=236,
                               blank=False, null=False)
    postal_code = models.CharField(max_length=10, validators=[validators.MinLengthValidator(10)],
                                   blank=True, null=True, verbose_name='Postal Code')
    phone_number = models.CharField(max_length=11, validators=[validators.MinLengthValidator(11)],
                                    blank=False, null=False, verbose_name='Phone Number')
    plate_number = models.CharField(max_length=10,
                                    blank=False, null=False, verbose_name='Plate Number')
    unit_number = models.CharField(max_length=10,
                                   blank=False, null=False, verbose_name='Unit Number')
    is_default = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='Is Default')
    submit_date = models.DateTimeField(default=timezone.now,
                                       blank=False, null=False, verbose_name='Submit Date')

    class Meta:
        ordering =  ['user', '-is_default', '-submit_date']
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'Address: {self.title} /For: {self.user}'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            other_default = self.user.user_addresses.exclude(pk=self.pk).filter(is_default=True)
            if self.is_default:
                if other_default.exists():
                    other_default.update(is_default=False)
            else:
                if not other_default.exists():
                    self.is_default = True
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user = self.user
        is_default = self.is_default
        super().delete(*args, **kwargs)

        if is_default:
            next_default = user.user_addresses.first()
            if next_default:
                next_default.update(is_default=True)
