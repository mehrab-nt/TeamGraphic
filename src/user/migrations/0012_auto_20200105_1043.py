# Generated by Django 3.0.1 on 2020-01-05 07:13

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0011_customer_rule'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Customer',
            new_name='User_TG',
        ),
    ]