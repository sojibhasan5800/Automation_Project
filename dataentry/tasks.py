from automation_dj.celery import app
from django.core.management import call_command
from .utlis import send_email_notification,generate_csv_file
from notifications_app.models import BroadcastNotification

import time

@app.task
def import_data_task(file_path, model_name,user_email,user_id):
    try:
        call_command('importdata', file_path, model_name)
    except Exception as e:
        raise e
    # notify the user by email
    mail_subject = 'Import Data Completed'
    message = 'Your data import has been successful'
    to_email = user_email
    # print(to_email)
    send_email_notification(mail_subject, message, [to_email])
    BroadcastNotification.objects.create(
        user_id=user_id,
        message=f"Your {model_name} data import has been completed successfully."
        )
    return 'Data imported successfully.'


@app.task
def export_data_task(model_name,user_email,user_id):
    try:
        call_command('exportdata', model_name)
    except Exception as e:
        raise e
    
    file_path = generate_csv_file(model_name)
    # Send email with the attachment
    mail_subject = 'Export Data Successful'
    message = 'Export data successful. Please find the attachment'
    to_email = user_email
    send_email_notification(mail_subject, message, [to_email], attachment=file_path)
    BroadcastNotification.objects.create(
        user_id=user_id,
        message=f"Your {model_name} data Export has been completed successfully."
        )
    return 'Export Data task executed successfully.'