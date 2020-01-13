# Generated by Django 3.0.1 on 2020-01-09 08:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0004_auto_20200107_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slideshow',
            name='link',
            field=models.CharField(default='/', max_length=20, validators=[django.core.validators.MinLengthValidator(1)]),
        ),
    ]