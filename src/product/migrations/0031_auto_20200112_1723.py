# Generated by Django 3.0.1 on 2020-01-12 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0030_auto_20200112_1648'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='design',
            name='base',
        ),
        migrations.RemoveField(
            model_name='design',
            name='low_price',
        ),
    ]
