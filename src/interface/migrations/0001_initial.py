# Generated by Django 3.0.1 on 2020-01-05 14:23

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import interface.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0024_auto_20200104_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20, validators=[django.core.validators.MinLengthValidator(3)])),
                ('link', models.CharField(max_length=20, validators=[django.core.validators.MinLengthValidator(2)])),
                ('rank', models.PositiveSmallIntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SlidShow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(3)])),
                ('image', models.ImageField(upload_to=interface.models.slide_show_directory_path)),
                ('rank', models.PositiveSmallIntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('link', models.CharField(max_length=20, validators=[django.core.validators.MinLengthValidator(2)])),
                ('active', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=50)),
                ('time', models.FloatField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
            ],
        ),
        migrations.CreateModel(
            name='SpecialProductBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveSmallIntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)])),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
    ]
