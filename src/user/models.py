from django.db import models
from django.utils import timezone
# from django.contrib.postgres.fields import *
from django.dispatch import receiver
import os


def user_profile_directory_pass(instance, filename):
    return './user/static/img/profile/{0}-profile.jpg'.format(instance.mobile)


class User(models.Model):
    mobile = models.CharField(primary_key=True, max_length=11, verbose_name='Mobile Number')
    password = models.CharField(max_length=20)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    confirm_code = models.CharField(max_length=4, null=True)
    email = models.CharField(blank=True, max_length=50)
    Profile = models.ImageField(upload_to=user_profile_directory_pass, blank=True, verbose_name='Profile Image')
    # point = models.IntegerField(default=0)
    reg_time = models.DateTimeField(default=timezone.now)
    last_edit_time = models.DateTimeField(auto_now=True)
    # intro_code
    # inv_code


@receiver(models.signals.post_delete, sender=User)
def auto_delete_classification_img_on_delete(sender, instance, **kwargs):
    if instance.Profile:
        if os.path.isfile(instance.Profile.path):
            os.remove(instance.Profile.path)


@receiver(models.signals.pre_save, sender=User)
def auto_delete_classification_img_on_change(sender, instance, **kwargs):
    if not instance.mobile:
        return False
    try:
        old_profile = User.objects.get(pk=instance.mobile).Profile
    except User.DoesNotExist:
        return False
    new_profile = instance.Profile
    if not old_profile == new_profile:
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
    detail = models.CharField(max_length=313, verbose_name='Address')
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name='user_addresses')

