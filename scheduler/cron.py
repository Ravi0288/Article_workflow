# scheduler/cron.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from functools import wraps
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.urls import reverse
from .models import SchedulerLog
import time
import logging



# Create logger
logger = logging.getLogger(__name__)


# List all the steps that need to be executed
# This should match the view names
STEP_NAMES = [
    # step1 URLs
    'download-from-ftp',
    'download-from-sftp',
    'download-from-submission-api',
    'download-from-crossref-api',
    'download-from-chorus-api',
    'action-deposites',
    
    # step2 URLs
    'migrate-to-step-2',
    # step3 URLs
    'migrate-to-step-3',
    # step4 URLs
    'migrate-to-step-4',
    # step5 URLs
    'migrate-to-step-5',
    # step6 URLs
    'migrate-to-step-6',
    # step7 URLs
    'migrate-to-step-7',
    # step8 URLs
    'migrate-to-step-8',
    # step9 URLs
    'migrate-to-step-9',
    # step10 URLs
    'migrate-to-step-10',
    # step11 URLs
    'migrate-to-step-11',
    # step12 URLs
    'migrate-to-step-12',
]


# Function to build full URL for a given view name
# This will use the BASE_BACKEND_URL setting to construct the full URL
def build_full_url(view_name):
    try:
        path = reverse(view_name)
        return f"{settings.BASE_URL}{path}"
    except Exception as e:
        logger.error(f"Could not reverse {view_name}: {e}")
        return None



# Function to call the step URL
# This will log success or failure of the HTTP request
def call_step(view_name, url):
    """
    Calls the step and logs its execution in SchedulerLog.
    """
    log_entry = SchedulerLog.objects.create(
        step=view_name,
        start_time=datetime.now(),
        status="SUCCESS"  # default, will update if failed
    )
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except Exception as e:
        log_entry.status = "FAILED"
        log_entry.error_message = str(e)
        log_entry.end_time = datetime.now()
        log_entry.save()
        logger.error(f"Step {view_name} failed: {e}")
        return False

    log_entry.status = "SUCCESS"
    log_entry.end_time = datetime.now()
    log_entry.save()
    logger.info(f"Step {view_name} completed successfully")
    return True


# Function to run all steps in sequence
# This will iterate through the STEP_NAMES, build the URL, and call each step
def run_all_steps_in_sequence():
    """
    Runs all steps sequentially. Stops if a step fails.
    """
    for view_name in STEP_NAMES:
        url = build_full_url(view_name)
        if not url:
            continue
        success = call_step(view_name, url)
        if not success:
            break
        time.sleep(2)


# Wrapper to log start and end time of the running job
def log_job_times(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger.info(f"Starting job: {func.__name__} at {start_time}")
        try:
            return func(*args, **kwargs)
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Finished job: {func.__name__} at {end_time} (Duration: {duration:.2f}s)")
    return wrapper


# accepted interval by apscheduler are
    # seconds	Run every N seconds
    # minutes	Run every N minutes
    # hours	    Run every N hours
    # days	    Run every N days
    # weeks	    Run every N weeks


# Function to register scheduled task and execute
@log_job_times
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all_steps_in_sequence, 'interval', days=30)
    scheduler.start()
    logger.info("Scheduler started")