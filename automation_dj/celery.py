import os

from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automation_dj.settings')

app = Celery('automation_dj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Set timezone
app.conf.enable_utc = False
app.conf.timezone = 'Asia/Dhaka'

# Optional: beat schedule
app.conf.beat_schedule = {
    # Example:
    # 'broadcast-every-day-4am': {
    #     'task': 'notifications_app.tasks.broadcast_notification',
    #     'schedule': crontab(hour=4, minute=0),
    #     'args': ()
    # }
}


# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
