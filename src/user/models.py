from django.db import models
from django.utils import timezone


class User(models.Model):
    mobile = models.CharField(primary_key=True, max_length=11, verbose_name='Mobile Number')
    password = models.CharField(max_length=20)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    confirm_code = models.CharField(max_length=4, null=True)
    email = models.CharField(blank=True, max_length=50)
    Profile = models.ImageField(blank=True, verbose_name='Profile Image')
    # point = models.IntegerField(default=0)
    reg_time = models.DateTimeField(default=timezone.now)
    last_edit_time = models.DateTimeField(auto_now=True)
    # intro_code
    # inv_code


class Country(models.TextChoices):
    IRAN = 'IRI', 'ایران'


class State(models.TextChoices):
    TEHRAN = 'TEH', 'تهران'


class Address(models.Model):
    country = models.CharField(max_length=3, choices=Country.choices, default=Country.IRAN)
    state = models.CharField(max_length=3, choices=State.choices, default=State.TEHRAN)
    # city =
    # area = models.CharField(max_length=25, blank=True)
    detail = models.CharField(max_length=313, verbose_name='Address')
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name='user_addresses')

