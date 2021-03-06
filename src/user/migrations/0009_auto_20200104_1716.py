# Generated by Django 3.0.1 on 2020-01-04 13:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('order', '0007_remove_cart_user'),
        ('user', '0008_auto_20200104_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('confirm_code', models.CharField(max_length=4, null=True)),
                ('Profile', models.ImageField(blank=True, upload_to=user.models.user_profile_directory_pass, verbose_name='Profile Image')),
            ],
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_addresses', to='user.Customer'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
