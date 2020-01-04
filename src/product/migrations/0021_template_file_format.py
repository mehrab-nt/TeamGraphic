# Generated by Django 3.0.1 on 2020-01-04 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0020_auto_20200104_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='template_file',
            name='format',
            field=models.CharField(choices=[('psd', 'PSD'), ('cdr', 'Corel'), ('ai', 'ILLUSTRATOR'), ('pdf', 'PDF')], default='psd', max_length=3),
        ),
    ]
