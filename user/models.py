from django.db import models
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True, validators=[validators.MinLengthValidator(11)],
                                    blank=False, null=False, verbose_name='Phone Number')
    national_id = models.CharField(max_length=10, unique=True, validators=[validators.MinLengthValidator(10)], blank=True, null=True,
                                   verbose_name='National ID')
    public_key = models.CharField(max_length=8, validators=[validators.MinLengthValidator(8)],
                                  blank=False, null=False, verbose_name='Public Key')
    private_key = models.CharField(max_length=20, blank=False, null=False, verbose_name='Private Key')
    accounting_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name='Accounting ID')
    accounting_name = models.CharField(max_length=73, blank=True, null=True, verbose_name='Accounting Name')
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name='role_all_users')
    is_employee = models.BooleanField(default=False,
                                      blank=False, null=False, verbose_name='Is Employee')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f'#{self.pk}: {self.first_name} {self.last_name} ({self.phone_number})'


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
    job = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        ordering = ['user']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile: {self.user}"


class Role(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name='Sort Number')

    class Meta:
        ordering = ['title']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return f'Role: {self.title}'


class Introduction(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    number = models.PositiveIntegerField(default=0, blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name='Sort Number')

    class Meta:
        ordering = ['-sort_number']
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
    # location
    state = models.CharField(max_length=37,
                             blank=True, null=True)
    city = models.CharField(max_length=37,
                            blank=True, null=True)
    content = models.TextField(max_length=300,
                               blank=False, null=False)
    postal_code = models.CharField(max_length=10, validators=[validators.MinLengthValidator(11)],
                                   blank=True, null=True, verbose_name='Postal Code')
    phone_number = models.CharField(max_length=11, validators=[validators.MinLengthValidator(11)],
                                    blank=False, null=False, verbose_name='Phone Number')
    plate_number = models.CharField(max_length=10,
                                    blank=False, null=False, verbose_name='Plate Number')
    unit_number = models.CharField(max_length=10,
                                   blank=False, null=False, verbose_name='Unit Number')
    is_default = models.BooleanField(default=False,
                                     blank=False, null=False, verbose_name='Is Default')
    submit_date = models.DateField(default=timezone.now,
                                   blank=False, null=False, verbose_name='Submit Date')

    class Meta:
        ordering = ['is_default', '-submit_date']
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'Address: {self.title} /For: {self.user}'
