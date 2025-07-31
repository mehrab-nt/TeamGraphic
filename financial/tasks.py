from celery import shared_task
from .models import CashBack
import jdatetime
from django.utils import timezone


@shared_task
def run_monthly_cashback_rollover():
    jalali_today = jdatetime.date.fromgregorian(date=timezone.now().date())
    if jalali_today.day != 1:
        return  # MEH: Only run on the 1st of each Jalali month
    for cashback in CashBack.objects.select_related('credit__owner').all():
        cashback.set_cashback_in_history()
