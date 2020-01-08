# Generated by Django 3.0.1 on 2020-01-04 12:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20200104_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='detail',
            field=models.CharField(max_length=313, validators=[django.core.validators.MinLengthValidator(10)], verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(blank=True, max_length=50, validators=[django.core.validators.EmailValidator]),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=30, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
        migrations.AlterField(
            model_name='user',
            name='mobile',
            field=models.CharField(max_length=11, primary_key=True, serialize=False, validators=[django.core.validators.MinLengthValidator(11)], verbose_name='Mobile Number'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=20, validators=[django.core.validators.MinLengthValidator(8)]),
        ),
    ]