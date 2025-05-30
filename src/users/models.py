from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import validators
from api.models import ApiItem


class GENDER(models.TextChoices):
    MALE = 'M'
    FEMALE = 'F'
    UNDEFINED = 'U'


class Employee(models.Model):
    phone_number = models.CharField(primary_key=True, max_length=11, validators=[validators.MinLengthValidator(11)],
                                    unique=True, blank=False, null=False, verbose_name="Phone Number")
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='employee_profile')
    national_id = models.CharField(max_length=10, unique=True, validators=[validators.MinLengthValidator(10)],
                                   blank=True, null=True, verbose_name="National ID")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Birth Date")
    gender = models.CharField(max_length=1, choices=GENDER.choices, default=GENDER.UNDEFINED, blank=False, null=False)
    # profile_image = models.ImageField(upload_to='profile_images', blank=True, null=True)
    level = models.ForeignKey("EmployeeLevel", on_delete=models.PROTECT, blank=True, null=True,
                              related_name="employees")

    class Meta:
        ordering = ['-user__date_joined']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f'Employee: {self.user.first_name} {self.user.last_name}'


class EmployeeLevel(models.Model):
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")
    api_items = models.ManyToManyField(
        ApiItem,
        through='EmployeeLevelApiItemAccess',
        through_fields=('employee_level', 'api_item'),
        verbose_name="Api Items"
    )

    class Meta:
        verbose_name = "Employee Level"
        verbose_name_plural = "Employee Levels"

    def __str__(self):
        return f'Employee Level: {self.title}'


class EmployeeLevelApiItemAccess(models.Model):
    employee_level = models.ForeignKey(EmployeeLevel, on_delete=models.CASCADE,
                                       related_name='all_api_items',)
    api_item = models.ForeignKey(ApiItem, on_delete=models.CASCADE,
                                 related_name='all_employee_levels',)

    class Meta:
        verbose_name = "Employee Level API Item Access"
        verbose_name_plural = "Employee Level API Items Access"

    def __str__(self):
        return f'{self.employee_level} Access for {self.api_item}'


class UserProfile(models.Model):
    phone_number = models.CharField(primary_key=True, max_length=11, validators=[validators.MinLengthValidator(11)],
                                    unique=True, blank=False, null=False, verbose_name="Phone Number")
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='user_profile')
    role = models.ForeignKey('Role', on_delete=models.PROTECT, blank=True, null=True,
                                  related_name='role_all_users')
    national_id = models.CharField(max_length=10, unique=True, validators=[validators.MinLengthValidator(10)],
                                   blank=True, null=True, verbose_name="National ID")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Birth Date")
    gender = models.CharField(max_length=1, choices=GENDER.choices, default=GENDER.UNDEFINED, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    public_key = models.CharField(max_length=8, validators=[validators.MinLengthValidator(8)],
                                  blank=False, null=False, verbose_name="Public Key")
    private_key = models.CharField(max_length=20, blank=False, null=False, verbose_name="Private Key")
    accounting_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name="Accounting ID")
    accounting_name = models.CharField(max_length=73, blank=True, null=True, verbose_name="Accounting Name")
    last_order_date = models.DateField(blank=True, null=True, verbose_name="Last Order Date")
    introduce_from = models.ForeignKey('Introduction', on_delete=models.PROTECT, blank=True, null=True, verbose_name="Introduction from",
                                       related_name='introduce_all_users')
    job = models.CharField(max_length=25, blank=True, null=True)
    total_order = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Total Order")
    last_order = models.DateField(blank=True, null=True, verbose_name="Last Order")
    total_main_buy = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Total Main Buy")
    total_option_buy = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Total Option Buy")


    class Meta:
        ordering = ['user__date_joined']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.user_profile.phone_number}: {self.user.first_name}"

    def user_full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def user_email_address(self):
        return self.user.email

    def is_active(self):
        return self.user.is_active
    is_active.boolean = True


class Role(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)


class Address(models.Model):
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False,
                             related_name='user_addresses')
    # location
    state = models.CharField(max_length=37, blank=True, null=True)
    city = models.CharField(max_length=37, blank=True, null=True)
    content = models.TextField(max_length=300, blank=False, null=False)
    postal_code = models.CharField(max_length=10, validators=[validators.MinLengthValidator(11)],
                                   blank=True, null=True)
    phone_number = models.CharField(max_length=11, validators=[validators.MinLengthValidator(11)],
                                    blank=False, null=False)
    plate_number = models.CharField(max_length=7, blank=False, null=False)
    unit_number = models.CharField(max_length=7, blank=False, null=False)
    is_default = models.BooleanField(default=False, blank=False, null=False)
    submit_date = models.DateField(default=timezone.now, blank=False, null=False, verbose_name="Submit Date")

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'Address: {self.title} User: {self.user.username}'


class Introduction(models.Model):
    title = models.CharField(max_length=25, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    number = models.PositiveIntegerField(default=0, blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Introduce'
        verbose_name_plural = 'Introduces'
