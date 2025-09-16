from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

class BroadcastNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
        )
    message = models.TextField()
    broadcast_on = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-broadcast_on']
    
    def __str__(self):
        return f"Notification {self.id} - {self.broadcast_on}"


@receiver(post_save, sender=BroadcastNotification)
def notification_handler(sender, instance, created, **kwargs):
    if created:
        # Import task locally to prevent circular import
        from .tasks import broadcast_notification  

        # Add 1 minute after creation (Asia/Dhaka time)
        run_time = instance.broadcast_on + timedelta(minutes=1)

        # # Convert to UTC to match Celery Beat crontab
        # run_time = instance.broadcast_on.astimezone(timezone.utc)

        # Convert run_time to UTC because Celery Beat Crontab uses UTC internally
        run_time_utc = run_time.astimezone(timezone.utc)

        # Create or get crontab schedule for the run_time_utc
        schedule, _ = CrontabSchedule.objects.get_or_create(
            hour=str(run_time_utc.hour),
            minute=str(run_time_utc.minute),
            day_of_month=str(run_time_utc.day),
            month_of_year=str(run_time_utc.month),
            day_of_week="*",
            timezone="UTC",   # Celery beat expects UTC
        )

        #  # ClockedSchedule Create
        # clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=run_time)

        # Create periodic task with enabled=True
        PeriodicTask.objects.create(
            crontab=schedule,
            name=f"broadcast-notification-{instance.id}",
            task="notifications_app.tasks.broadcast_notification",
            args=json.dumps([instance.id,instance.user.id]),  # JSON list
            enabled=True, 
            one_off=True,
        )

        print(f"BroadcastNotification scheduled for {run_time} Asia/Dhaka → {run_time_utc} UTC")
