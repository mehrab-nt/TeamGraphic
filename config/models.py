from django.db import models
from django.core import validators
from landing.models import Landing, Metadata
from user.models import Role
from django.utils import timezone


class GoogleCodeType(models.TextChoices):
    UA = 'UA'
    GA4 = 'GA$'


class MainPageConfig(models.Model):
    company_name = models.CharField(max_length=78,
                                    blank=False, null=False, verbose_name='Company Name')
    phone_number = models.CharField(max_length=23, blank=True, null=True,
                                    verbose_name='Phone Number')
    # header_logo = models.ImageField(upload_to='logo', blank=True, null=True)
    # social_logo = models.ImageField(upload_to='logo', blank=True, null=True)
    # footer_logo = models.ImageField(upload_to='logo', blank=True, null=True)
    # fav_icon = models.ImageField(upload_to='logo', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    social_media = models.JSONField(default=dict,
                                    blank=True, null=True, verbose_name='Social Media')
    address = models.TextField(max_length=300,
                               blank=True, null=True)
    wellcome_massage = models.TextField(max_length=300,
                                        blank=True, null=True, verbose_name='Wellcome Massage')
    login_massage = models.TextField(max_length=300,
                                     blank=True, null=True, verbose_name='Login Massage')
    rules_page = models.ForeignKey(Landing, on_delete=models.SET_NULL,
                                   blank=True, null=True, verbose_name='Rules Page',
                                   related_name='main_config')
    rules_page_check = models.BooleanField(default=False,
                                           blank=False, null=False, verbose_name='Rules Page Check')
    about_me = models.TextField(max_length=1092,
                                blank=True, null=True, verbose_name='About Me')
    metadate = models.ForeignKey(Metadata, on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 verbose_name='main_page')
    google_code = models.CharField(max_length=23,
                                   blank=True, null=True, verbose_name='Google Code')
    google_code_type = models.CharField(max_length=3,
                                        choices=GoogleCodeType.choices, default=GoogleCodeType.UA,
                                        blank=True, null=True, verbose_name='Google Code Type')
    robots_txt = models.TextField(max_length=1092,
                                  blank=True, null=True, verbose_name='robots.txt')
    redirect_list = models.JSONField(default=dict,
                                     blank=True, null=True, verbose_name='Redirect List')

    class Meta:
        verbose_name = 'Main Page'
        verbose_name_plural = 'Main Pages'

    def __str__(self):
        return f'Main Page: {self.company_name}'


class ViewType(models.TextChoices):
    BLOCK = 'BLK'
    LIST = 'LIS'

def price_list_upload_path(instance, filename): # MEH: Upload File here (with safe slug name)
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    return f'price-list/TG-{timestamp}.pdf'


class PriceListConfig(models.Model):
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    view_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                 choices=ViewType.choices, default=ViewType.BLOCK,
                                 blank=False, null=False, verbose_name='View Type')
    auth_need = models.BooleanField(default=False,
                                    blank=False, null=False, verbose_name='Auth Need')
    block_role = models.ManyToManyField(Role, blank=True,
                                        verbose_name='Block Role')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Last Update')
    last_pdf_update = models.DateTimeField(blank=True, null=True, verbose_name='Last Pdf Update')
    pdf_file = models.FileField(upload_to=price_list_upload_path,
                                blank=True, null=True, verbose_name='PDF File')


class MessageConfig(models.Model):
    order_message = models.BooleanField(default=True,
                                        blank=False, null=False, verbose_name='Order Message')
    order_message_description = models.TextField(max_length=1378,
                                                 blank=True, null=True, verbose_name='Order Message Description')
    support_message_description = models.TextField(max_length=1378,
                                                   blank=True, null=True, verbose_name='Support Message Description')
    tracking_message_description = models.TextField(max_length=1378,
                                                    blank=True, null=True, verbose_name='Tracking Message Description')
    point_message_description = models.TextField(max_length=1378,
                                                 blank=True, null=True, verbose_name='Point Message Description')
