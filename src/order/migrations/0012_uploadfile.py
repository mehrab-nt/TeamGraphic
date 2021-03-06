# Generated by Django 3.0.1 on 2020-01-12 14:28

from django.db import migrations, models
import django.db.models.deletion
import order.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_auto_20200107_1243'),
        ('order', '0011_auto_20200112_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(choices=[('front', 'رو'), ('back', 'پشت'), ('front_film', 'فیلم رو'), ('back_film', 'فیلم پشت'), ('front_gold', 'طلاکوب رو'), ('back_gold', 'طلاکوب پشت'), ('front_form', 'قالب رو'), ('back_form', 'قالب پشت')], max_length=22)),
                ('file', models.ImageField(upload_to=order.models.order_upload_file_directory_path)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_files', to='order.Order')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_files', to='user.UserTG')),
            ],
        ),
    ]
