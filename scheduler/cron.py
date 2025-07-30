from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
import logging, requests
import os
from .models import SchedulerLog
from functools import wraps
import traceback

# Import all step functions
from step1.action_deposites import file_transfer_from_deposites
from step1.download_from_ftp import download_from_ftp
from step1.download_from_sftp import download_from_sftp
from step1.submission_api import download_from_submission_api
from step1.chorus_api import download_from_chorus_api
from step1.crossref_api import download_from_crossref_api 

from step2.article import migrate_to_step2
from step3.migrate_to_step_3 import migrate_to_step3, update_journal_model
from step4.migrate_to_step_4 import migrate_to_step4
from step5.migrate_to_step_5 import migrate_to_step5
from step6.migrate_to_step_6 import migrate_to_step6
from step7.migrate_to_step_7 import migrate_to_step7
from step8.migrate_to_step8 import migrate_to_step8
from step9.migrate_to_step_9 import migrate_to_step9
from step10.migrate_to_step_10 import migrate_to_step10
from step11.migrate_to_step_11 import migrate_to_step11
from step12.migrate_to_step12 import migrate_to_step12

logger = logging.getLogger(__name__)

# STEP FUNCTIONS
STEP_FUNCTIONS = [
    download_from_ftp,
    download_from_sftp,
    download_from_submission_api,
    download_from_crossref_api,
    download_from_chorus_api,
    file_transfer_from_deposites,

    migrate_to_step2,

    migrate_to_step3,
    update_journal_model,

    migrate_to_step4,

    migrate_to_step5,

    migrate_to_step6,

    migrate_to_step7,

    migrate_to_step8,

    migrate_to_step9,

    migrate_to_step10,

    migrate_to_step11,

    migrate_to_step12
]

#  Wrapper to calcaulate time taken by any process
def log_job_times(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = timezone.now()
        logger.info(f"Starting job: {func.__name__} at {start_time}")
        try:
            return func(*args, **kwargs)
        finally:
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Finished job: {func.__name__} at {end_time} (Duration: {duration:.2f}s)")
    return wrapper


# Function to call steps
@log_job_times
def call_step(request):
    """
    Call each step function with the provided `request` and log.
    """
    for step_func in STEP_FUNCTIONS:
        step_name = step_func.__name__
        print(step_name, "Execution started")
        log_entry = SchedulerLog.objects.create(
            step=step_name,
            start_time=timezone.now(),
            status="PENDING"
        )
        try:
            step_func(request)   # Now we always pass the real request
            log_entry.status = "SUCCESS"
            logger.info(f"Step {step_name} completed successfully")
        except Exception as e:
            log_entry.status = "FAILED"
            log_entry.error_message = f"{str(e)}\n\n{traceback.format_exc()}"
            logger.error(f"step {step_name} failed: {e}")
            log_entry.end_time = timezone.now()
            log_entry.save()
            return False

        print(step_name, "Execution Ended")
        log_entry.end_time = timezone.now()
        log_entry.save()
    return True


# Funtion to manully trigger call_step function
def trigger_scheduler(request):
    """
    This view manually triggers the scheduler task (also called by APScheduler).
    """
    call_step(request)
    return JsonResponse({"message": "Scheduler triggered successfully!"})


# Scheduler
def start():
    """
    Scheduler now calls the trigger_scheduler URL with requests.get()
    so that a proper Django `request` is used.
    """
    def call_trigger_url():
        url = os.path.join(settings.BASE_URL, "scheduler/trigger-scheduler/")
        logger.info(f"Scheduler calling {url}")
        response = requests.get(url, timeout=9000)
        if response.status_code != 200:
            logger.error(f"Trigger failed: {response.text}")

    scheduler = BackgroundScheduler()

    # accepted interval by apscheduler are
        # seconds	Run every N seconds
        # minutes	Run every N minutes
        # hours	    Run every N hours
        # days	    Run every N days
        # weeks	    Run every N weeks

    # An interval job if you want it to run every 2nd week from days of server start
    # scheduler.add_job(call_trigger_url, 'interval', week=2)

    # An interval job if you want it to run every 30 days from days of server start
    scheduler.add_job(call_trigger_url, 'interval', days=30)


    #  accepted cron parameters by apscheduler are
        # year	    Run every year at the specified time
        # month	    Run every month at the specified time
        # day	    Run every day at the specified time
        # week	    Run every week at the specified time
        # day_of_week	Run on a specific day of the week
        # hour	    Run at a specific hour
        # minute	Run at a specific minute
        # second	Run at a specific second
        
    # Schedule the job to run every 30 days at 2:00 AM
    # scheduler.add_job(call_trigger_url,'cron', day=30,hour=2,minute=0)

    # Schedule the job to run every 30 and 15 days of the month at 2:00 AM
    # scheduler.add_job(call_trigger_url,'cron', day='15,30', hour=2,minute=0)

    # Schedule the job to run every day at 2:00 AM
    # scheduler.add_job(call_trigger_url,'cron', hour=2,minute=0)

    scheduler.start()
    logger.info("Scheduler started and will call trigger_scheduler URL")
