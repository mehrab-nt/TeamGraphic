# Generated by Django 3.0.1 on 2020-01-04 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20200104_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='Profile',
            field=models.ImageField(blank=True, upload_to='./user/static/img/profile', verbose_name='Profile Image'),
        ),
    ]
