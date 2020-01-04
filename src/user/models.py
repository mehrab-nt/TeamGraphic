from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# from django.contrib.postgres.fields import *
from django.dispatch import receiver
from django.core import validators
import os


def user_profile_directory_pass(instance, filename):
    return './user/static/img/profile/{0}-profile.jpg'.format(instance.user.username)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # mobile = models.CharField(primary_key=True, max_length=11, verbose_name='Mobile Number',
    #                           validators=[validators.MinLengthValidator(11)])
    # password = models.CharField(max_length=20, validators=[validators.MinLengthValidator(8)])
    # first_name = models.CharField(max_length=30, validators=[validators.MinLengthValidator(3)])
    # last_name = models.CharField(max_length=30, validators=[validators.MinLengthValidator(3)])
    confirm_code = models.CharField(max_length=4, null=True)
    # email = models.CharField(blank=True, max_length=50, validators=[validators.EmailValidator()])
    profile = models.ImageField(upload_to=user_profile_directory_pass, blank=True, verbose_name='Profile Image')
    # point = models.IntegerField(default=0)
    # reg_time = models.DateTimeField(default=timezone.now)
    # last_edit_time = models.DateTimeField(auto_now=True)
    # intro_code
    # inv_code

    def __str__(self):
        return 'User-{0}'.format(self.user.username)

    def customer_full_name(self):
        return '{0} - {1}'.format(self.user.first_name, self.user.last_name)

    def customer_email_address(self):
        return self.user.email

    def is_active(self):
        return self.user.is_active


@receiver(models.signals.post_delete, sender=Customer)
def auto_delete_classification_img_on_delete(sender, instance, **kwargs):
    if instance.Profile:
        if os.path.isfile(instance.Profile.path):
            os.remove(instance.Profile.path)


@receiver(models.signals.pre_save, sender=Customer)
def auto_delete_classification_img_on_change(sender, instance, **kwargs):
    if not instance.user:
        return False
    try:
        old_profile = Customer.objects.get(pk=instance.user).Profile
    except Customer.DoesNotExist:
        return False
    new_profile = instance.Profile
    if not old_profile == new_profile and old_profile:
        if os.path.isfile(old_profile.path):
            os.remove(old_profile.path)


class Country(models.TextChoices):
    IRAN = 'IRI', 'ایران'


class State(models.TextChoices):
    TEHRAN = 'TEH', 'تهران'


class Address(models.Model):
    country = models.CharField(max_length=3, choices=Country.choices, default=Country.IRAN)
    state = models.CharField(max_length=3, choices=State.choices, default=State.TEHRAN)
    # city =
    # area = models.CharField(max_length=25, blank=True)
    detail = models.CharField(max_length=313, verbose_name='Address', validators=[validators.MinLengthValidator(10)])
    user = models.ForeignKey('Customer', on_delete=models.CASCADE,
                             related_name='user_addresses')

    def __str__(self):
        return 'User-{0}'.format(self.user.user.username)

