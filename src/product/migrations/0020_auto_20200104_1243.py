# Generated by Django 3.0.1 on 2020-01-04 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0019_auto_20200104_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template_file',
            name='title',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
