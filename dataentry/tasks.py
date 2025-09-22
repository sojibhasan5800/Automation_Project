from automation_dj.celery import app
from django.core.management import call_command
from .utlis import send_email_notification,generate_csv_file,async_read_csv,async_write_csv
from notifications_app.models import BroadcastNotification

import time

@app.task
def import_data_task(file_path, model_name, user_email, user_id):
    import asyncio
    from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
    from django.apps import apps
    from .utlis import send_email_notification, process_csv_cpu
    from notifications_app.models import BroadcastNotification

    # ==================== Step 1: New event loop ====================
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # ==================== Step 2: CPU-bound CSV processing using ProcessPoolExecutor ====================
    with ProcessPoolExecutor(max_workers=4) as executor:
        future = executor.submit(process_csv_cpu, file_path)
        processed_data = future.result()   # process_csv_cpu returns a list of dicts

    # ==================== Step 3: Save data to DB ====================
    model = apps.get_model('dataentry', model_name)
    for row in processed_data:
        model.objects.create(**row)

    # ==================== Step 4: Send Email concurrently using ThreadPoolExecutor ====================
    mail_subject = 'Import Data Completed'
    message = f'Your {model_name} data import has been successful'
    to_email = [user_email]
    with ThreadPoolExecutor(max_workers=3) as pool:
        pool.submit(send_email_notification, mail_subject, message, to_email)

    # ==================== Step 5: Broadcast Notification ====================
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


# CPU-bound CSV processing
def process_csv_cpu(file_path):
    import csv
    data = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # pretend CPU-heavy task
            row = {k:v.upper() if isinstance(v,str) else v for k,v in row.items()}
            data.append(row)
    return data