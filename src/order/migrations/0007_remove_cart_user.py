# Generated by Django 3.0.1 on 2020-01-04 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_cart_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='user',
        ),
    ]
