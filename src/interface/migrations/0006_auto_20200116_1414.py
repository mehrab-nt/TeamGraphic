# Generated by Django 3.0.1 on 2020-01-16 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0005_auto_20200109_1158'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mainimage',
            options={'verbose_name': 'عکس های اصلی', 'verbose_name_plural': 'عکس های اصلی'},
        ),
        migrations.AlterModelOptions(
            name='mainmenu',
            options={'verbose_name': 'منو اصلی', 'verbose_name_plural': 'منو اصلی'},
        ),
        migrations.AlterModelOptions(
            name='slideshow',
            options={'verbose_name': 'اسلاید شو', 'verbose_name_plural': 'اسلاید شو'},
        ),
        migrations.AlterModelOptions(
            name='specialproductbox',
            options={'verbose_name': 'محصولات خاص', 'verbose_name_plural': 'محصولات خاص'},
        ),
    ]
