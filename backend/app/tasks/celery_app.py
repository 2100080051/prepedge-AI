"""
Celery task queue for background processing.
Handles async jobs like sending emails, indexing, etc.
"""

from celery import Celery, Task
from celery.schedules import crontab
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    'prepedge',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minute hard limit
    task_soft_time_limit=25 * 60,  # 25 minute soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    'index-new-jobs': {
        'task': 'app.tasks.jobs.index_new_jobs',
        'schedule': crontab(minute=0),  # Every hour
    },
    'update-trending-companies': {
        'task': 'app.tasks.analytics.update_trending_companies',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'clean-old-data': {
        'task': 'app.tasks.maintenance.clean_old_data',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'generate-recommendations': {
        'task': 'app.tasks.ml.generate_recommendations',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
}

class DatabaseTask(Task):
    """Task with database session support."""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True


# Define base task class
celery_app.Task = DatabaseTask

def get_celery_app() -> Celery:
    """Get Celery app instance."""
    return celery_app
