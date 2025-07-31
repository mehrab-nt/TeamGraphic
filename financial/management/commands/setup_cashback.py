from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Setup monthly cashback rollover task'

    def handle(self, *args, **kwargs):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_month='1',
            month_of_year='*',
            day_of_week='*',
            timezone='Asia/Tehran',
        )
        task, _ = PeriodicTask.objects.update_or_create(
            name='Run Monthly Cashback Rollover',
            defaults={
                'task': 'your_app.tasks.run_monthly_cashback_rollover',
                'crontab': schedule,
                'enabled': True,
            }
        )
        self.stdout.write(self.style.SUCCESS('Cashback rollover task created or updated'))
