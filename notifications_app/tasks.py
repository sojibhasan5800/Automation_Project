from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# from .models import BroadcastNotification
from .models import BroadcastNotification
import json
from celery import Celery, states
from asgiref.sync import async_to_sync
from celery.exceptions import Ignore
import asyncio


@shared_task(bind=True)
def broadcast_notification(self, notification_id,user_id):
    print("Task started with ID:", notification_id)
    try:
        # Queryset এর পরিবর্তে সরাসরি get ব্যবহার করো
        notification = BroadcastNotification.objects.get(id=int(notification_id))
        print("Notification found:", notification.message)

        channel_layer = get_channel_layer()
        print("Channel layer:", channel_layer)

        async_to_sync(channel_layer.group_send)(
            f"notification_{user_id}",
            {
                "type": "send_notification",
                "message": json.dumps({
                    "text": notification.message,
                    "type": "info"
                }),
            }
        )
        print("Message sent to group!")

        notification.sent = True
        notification.save()
        print("Notification updated as sent!")

        return "Done"

    except BroadcastNotification.DoesNotExist:
        print("Notification not found with ID:", notification_id)
        self.update_state(
            state="FAILURE",
            meta={"exe": "Not Found"}
        )
        raise Ignore()

    except Exception as e:
        print("Unexpected error in Celery Task:", str(e))
        import traceback
        print(traceback.format_exc())  

        self.update_state(
            state="FAILURE",
            meta={"exe": f"Failed: {str(e)}"}
        )
        raise Ignore()
