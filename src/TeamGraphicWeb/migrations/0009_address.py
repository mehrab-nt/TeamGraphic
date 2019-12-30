# Generated by Django 3.0.1 on 2019-12-30 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TeamGraphicWeb', '0008_auto_20191230_1433'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(choices=[('IRI', 'ایران')], default='IRI', max_length=3)),
                ('state', models.CharField(choices=[('TEH', 'تهران')], default='TEH', max_length=3)),
                ('detail', models.CharField(max_length=313, verbose_name='Address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_addresses', to='TeamGraphicWeb.User')),
            ],
        ),
    ]
