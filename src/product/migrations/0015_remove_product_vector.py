# Generated by Django 3.0.1 on 2020-01-04 09:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_auto_20200104_1226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='vector',
        ),
    ]