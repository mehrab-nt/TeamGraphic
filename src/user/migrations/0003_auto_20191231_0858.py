# Generated by Django 3.0.1 on 2019-12-31 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_remove_address_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='Profile',
            field=models.ImageField(blank=True, upload_to='', verbose_name='Profile Image'),
        ),
    ]