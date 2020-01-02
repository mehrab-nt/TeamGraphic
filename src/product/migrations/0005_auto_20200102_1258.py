# Generated by Django 3.0.1 on 2020-01-02 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_selling_option_side'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selling_option',
            name='side',
            field=models.PositiveSmallIntegerField(blank=True, choices=[('0', 'غیر فعال'), ('1', 'یک رو'), ('2', 'دو رو')], default='0'),
        ),
    ]