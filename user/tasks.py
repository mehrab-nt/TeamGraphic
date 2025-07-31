from celery import shared_task
import time  # simulate SMS delay


@shared_task
def send_phone_verification_code(code, phone_number):
    # MEH: todo: Sending SMS logic Here
    print(f"[SIMULATED SMS] To: {phone_number} | Code: {code}")
    time.sleep(5)
    return True
