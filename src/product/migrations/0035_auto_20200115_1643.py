# Generated by Django 3.0.1 on 2020-01-15 13:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0034_auto_20200114_1422'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sellingoption',
            options={'ordering': ['size', 'ready', 'count', '-side']},
        ),
        migrations.RenameField(
            model_name='service',
            old_name='description',
            new_name='hint',
        ),
        migrations.AddField(
            model_name='orderproductservices',
            name='description',
            field=models.CharField(blank=True, max_length=300, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
        migrations.AlterField(
            model_name='size',
            name='title',
            field=models.CharField(max_length=20, validators=[django.core.validators.MinLengthValidator(2)]),
        ),
    ]
