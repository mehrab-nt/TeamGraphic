# Generated by Django 3.0.1 on 2020-01-04 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_auto_20200104_1214'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_id',
        ),
        migrations.AddField(
            model_name='product',
            name='id',
            field=models.CharField(default=0, max_length=6, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
