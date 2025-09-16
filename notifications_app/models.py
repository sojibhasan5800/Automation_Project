from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from django.utils import timezone
from datetime import timezone

class BroadcastNotification(models.Model):
    message = models.TextField()
    broadcast_on = models.DateTimeField()
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

        # Convert to UTC to match Celery Beat crontab
        run_time = instance.broadcast_on.astimezone(timezone.utc)

        # Create or get crontab schedule for the broadcast time
        schedule, _ = CrontabSchedule.objects.get_or_create(
            hour=str(run_time.hour),
            minute=str(run_time.minute),
            day_of_month=str(run_time.day),
            month_of_year=str(run_time.month),
            day_of_week="*",
            timezone="UTC",
        )

        #  # ClockedSchedule Create
        # clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=run_time)

        # Create periodic task with enabled=True
        PeriodicTask.objects.create(
            crontab=schedule,
            name=f"broadcast-notification-{instance.id}",
            task="notifications_app.tasks.broadcast_notification",
            args=json.dumps([instance.id]),  # JSON list
            enabled=True, 
            one_off=True,
        )

        print(f"BroadcastNotification scheduled: {instance.id}")
