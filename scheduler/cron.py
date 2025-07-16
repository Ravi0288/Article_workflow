# scheduler/cron.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from functools import wraps


# Create logger
logger = logging.getLogger(__name__)


# Wrapper to log start and end time of the running job
def log_job_times(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger.info(f"Starting job: {func.__name__} at {start_time}")
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Finished job: {func.__name__} at {end_time} (Duration: {duration:.2f}s)")
    return wrapper


# Task 1
@log_job_times
def run_step_2():
    print(f"[{datetime.now()}] Running scheduled job 1...")

# Task 2
@log_job_times
def run_step_3():
    print(f"[{datetime.now()}] Running scheduled job 2...")


# Add all required scheduler here.

# accepted interval by apscheduler are
    # seconds	Run every N seconds
    # minutes	Run every N minutes
    # hours	    Run every N hours
    # days	    Run every N days
    # weeks	    Run every N weeks


# Function to register scheduled task and execute
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_step_2, 'interval', seconds=2)
    scheduler.add_job(run_step_3, 'interval', seconds=2)
    scheduler.start()
