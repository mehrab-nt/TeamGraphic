# Generated by Django 3.0.1 on 2019-12-31 09:36

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0001_initial'),
        ('order', '0005_auto_20191231_0912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='order',
            name='create_date',
        ),
        migrations.AddField(
            model_name='cart',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='cart',
            name='delivery',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='all_cart', to='delivery.Delivery'),
        ),
        migrations.AddField(
            model_name='cart',
            name='delivery_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='cart',
            name='duration',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cart',
            name='total_cost',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cart',
            name='status',
            field=models.CharField(choices=[('rec', 'در حال ثبت'), ('chk', 'در حال بررسی'), ('pre', 'آماده سازی'), ('rdy', 'آماده تحویل'), ('del', 'آماده ارسال'), ('snd', 'ارسال شد'), ('get', 'تحویل داده شد'), ('can', 'لغو شده'), ('rem', 'صورت حساب مانده')], default='rec', max_length=3),
        ),
        migrations.AlterField(
            model_name='order',
            name='cost',
            field=models.PositiveIntegerField(),
        ),
    ]