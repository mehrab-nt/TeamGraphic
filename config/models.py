from django.db import models
from landing.models import Landing, Metadata


class GoogleCodeType(models.TextChoices):
    UA = 'UA'
    GA4 = 'GA$'


class MainPage(models.Model):
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
