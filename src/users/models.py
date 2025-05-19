from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import validators
from financial.models import Company, Credit


class GENDER(models.TextChoices):
    MALE = 'M'
    FEMALE = 'F'
    UNDEFINED = 'U'


class UserProfile(models.Model):
    phone_number = models.CharField(primary_key=True, max_length=11, validators=[validators.MinLengthValidator(11)],
                                    unique=True, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    national_id = models.CharField(max_length=10, unique=True, validators=[validators.MinLengthValidator(10)],
                                   blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER.choices, default=GENDER.UNDEFINED, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    public_key = models.CharField(max_length=8, validators=[validators.MinLengthValidator(8)],
                                  blank=False, null=False)
    private_key = models.CharField(max_length=20, blank=False, null=False)
    accounting_id = models.IntegerField(blank=False, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    last_order_date = models.DateField(blank=True, null=True)
    how_to = models.CharField(max_length=25, blank=False, null=False)
    job = models.CharField(max_length=25, blank=True, null=True)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['user__date_joined']

    def __str__(self):
        return f"User {self.user.username}:{self.user.user_profile.phone_number}"


class Address(models.Model):
    address_name = models.CharField(max_length=25, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False)
    address_text = models.TextField(blank=False, null=False)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    # location
    phone_number = models.CharField(max_length=11, validators=[validators.MinLengthValidator(11)],
                                    blank=False, null=False)
    plate_number = models.CharField(max_length=7, blank=False, null=False)
    unit_number = models.CharField(max_length=7, blank=False, null=False)

