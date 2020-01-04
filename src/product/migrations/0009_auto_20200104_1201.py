# Generated by Django 3.0.1 on 2020-01-04 08:31

from django.db import migrations, models
import product.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_auto_20200104_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='design',
            name='id',
            field=models.CharField(max_length=3, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='preview',
            field=models.ImageField(upload_to=product.models.product_preview_directory_path),
        ),
        migrations.AlterField(
            model_name='product',
            name='vector',
            field=models.ImageField(blank=True, upload_to=product.models.product_vector_directory_path),
        ),
    ]
