# Generated by Django 3.0.1 on 2020-01-04 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_remove_product_vector'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='discount',
            field=models.PositiveIntegerField(blank=True, default=0),
            preserve_default=False,
        ),
    ]
