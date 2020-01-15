# Generated by Django 3.0.1 on 2020-01-15 13:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0035_auto_20200115_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='duration',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(30)]),
        ),
    ]