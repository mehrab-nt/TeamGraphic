# Generated by Django 3.0.1 on 2020-01-14 10:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0013_order_product_services'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='description',
            field=models.TextField(blank=True, max_length=777, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
    ]
