# Generated by Django 3.0.1 on 2020-01-04 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20200104_1652'),
        ('order', '0005_remove_cart_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_carts', to='user.User'),
        ),
    ]
