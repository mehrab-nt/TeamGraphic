# Generated by Django 3.0.1 on 2020-01-04 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import user.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0005_remove_cart_user'),
        ('user', '0006_auto_20200104_1551'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirm_code', models.CharField(max_length=4, null=True)),
                ('Profile', models.ImageField(blank=True, upload_to=user.models.user_profile_directory_pass, verbose_name='Profile Image')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
