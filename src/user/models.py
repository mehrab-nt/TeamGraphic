from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# from django.contrib.postgres.fields import *
from django.dispatch import receiver
from django.core import validators
import os


def user_profile_directory_pass(instance, filename):
    return './user/static/img/profile/{0}-profile.jpg'.format(instance.user.username)


class Role(models.TextChoices):
    CUSTOMER = 'csm', 'مشتری'
    COLLEAGUE = 'col', 'همکار'
    FORMAL_DESIGNER = 'fde', 'طراح'
    NON_FORMAL_DESIGNER = 'nde', 'طراح غیرحضوری'
    MANAGEMENT = 'man', 'مدیریت'
    OPERATOR = 'opr', 'اپراتور'
    INTERNAL_MANAGEMENT = 'pre', 'مدیریت داخلی'
    ACCOUNTANT = 'acc', 'حسابدار'
    IT = 'itm', 'مدیر سایت'
    NEW = 'new', 'عضو جدید'


class Introduction(models.Model):
    title = models.CharField(max_length=20, validators=[validators.MinLengthValidator(3)], unique=True)
    number = models.PositiveSmallIntegerField(default=0, blank=False)

    def __str__(self):
        return '{0}'.format(self.title)


class UserTG(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                                related_name='user_tg')
    role = models.CharField(max_length=3, choices=Role.choices, default=Role.CUSTOMER)
    # role = models.ForeignKey('Role', on_delete=models.SET_NULL,
    #                          related_name='all_user')
    # mobile = models.CharField(primary_key=True, max_length=11, verbose_name='Mobile Number',
    #                           validators=[validators.MinLengthValidator(11)])
    # password = models.CharField(max_length=20, validators=[validators.MinLengthValidator(8)])
    # first_name = models.CharField(max_length=30, validators=[validators.MinLengthValidator(3)])
    # last_name = models.CharField(max_length=30, validators=[validators.MinLengthValidator(3)])
    confirm_code = models.CharField(max_length=4, null=True)
    # email = models.CharField(blank=True, max_length=50, validators=[validators.EmailValidator()])
    profile = models.ImageField(upload_to=user_profile_directory_pass, blank=True, verbose_name='Profile Image')
    introduction = models.ForeignKey('Introduction', on_delete=models.SET_NULL, null=True, blank=False,
                                     related_name='all_user')
    # point = models.IntegerField(default=0)
    # reg_time = models.DateTimeField(default=timezone.now)
    # last_edit_time = models.DateTimeField(auto_now=True)
    # intro_code
    # inv_code

    def __str__(self):
        return 'User-{0}'.format(self.user.username)

    def user_full_name(self):
        return '{0} - {1}'.format(self.user.first_name, self.user.last_name)

    def user_email_address(self):
        return self.user.email

    def is_active(self):
        return self.user.is_active
    is_active.boolean = True

    def address_count(self, counter=0):
        for num in self.user_addresses.all():
            counter += 1
        return counter


@receiver(models.signals.post_delete, sender=UserTG)
def auto_delete_classification_img_on_delete(sender, instance, **kwargs):
    if instance.profile:
        if os.path.isfile(instance.profile.path):
            os.remove(instance.profile.path)


@receiver(models.signals.pre_save, sender=UserTG)
def auto_delete_classification_img_on_change(sender, instance, **kwargs):
    if not instance.user:
        return False
    try:
        old_profile = UserTG.objects.get(pk=instance.user).profile
    except UserTG.DoesNotExist:
        return False
    new_profile = instance.profile
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
    user = models.ForeignKey('UserTG', on_delete=models.CASCADE,
                             related_name='user_addresses')

    def __str__(self):
        return 'User-{0}'.format(self.user.user.username)


# class Role_TG(models.Model):
#     id = models.CharField(max_length=3, primary_key=True, validators=[validators.MinLengthValidator(3)])
#     title = models.CharField(max_length=20, validators=[validators.MinLengthValidator(3)])
#     access = models.ManyToManyRel()
#
#
# class Access(models.Model):
