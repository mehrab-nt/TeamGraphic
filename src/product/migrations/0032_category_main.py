# Generated by Django 3.0.1 on 2020-01-13 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0031_auto_20200112_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='main',
            field=models.BooleanField(default=False),
        ),
    ]