# scheduler/cron.py
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
import logging
from functools import wraps
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.urls import reverse
from .models import SchedulerLog
import time
import logging
import traceback
from django.http import JsonResponse



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
    

# Function to call each step and log the result
# This will make a GET request to the URL and log success or failure
def call_step(view_name, url):
    # Create initial log entry
    log_entry = SchedulerLog.objects.create(
        step=view_name,
        start_time=timezone.now(),
        status="PENDING"
    )

    try:
        response = requests.get(url, timeout=60)

        # Failure if step view returns 4xx or 5xx
        if response.status_code >= 400:
            error_details = response.text[:500]
            logger.error(f"Step {view_name} failed: {error_details}")
            raise Exception(
                f"Step '{view_name}' failed with status {response.status_code}. Details: {error_details}"
            )

        # Success if no exception
        log_entry.status = "SUCCESS"
        logger.info(f"Step {view_name} completed successfully with status {response.status_code}")
    except Exception as e:
        logger.error(f"Step {view_name} failed: {e}")
        log_entry.status = "FAILED"
        # Capture full traceback for debugging
        log_entry.error_message = f"{str(e)}\n\n{traceback.format_exc()}"

        # Stop scheduler on failure
        return False

    finally:
        log_entry.end_time = timezone.now()
        log_entry.save()

    return True


# Function to run all steps in sequence
# This will iterate through the STEP_NAMES, build the URL, and call each step
def run_all_steps_in_sequence():
    for view_name in STEP_NAMES:
        url = build_full_url(view_name)
        if not url:
            continue

        success = call_step(view_name, url)

        if not success:
            break  # stop further steps if one fails
        time.sleep(2)



# Wrapper to log start and end time of the running job
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


# accepted interval by apscheduler are
    # seconds	Run every N seconds
    # minutes	Run every N minutes
    # hours	    Run every N hours
    # days	    Run every N days
    # weeks	    Run every N weeks


## Function to register scheduled task and execute
@log_job_times
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all_steps_in_sequence, 'interval', days=30)
    scheduler.start()
    logger.info("Scheduler started")



def trigger_scheduler(request):
    run_all_steps_in_sequence()  # manually call the function
    return JsonResponse({"message": "Scheduler triggered manually!"})