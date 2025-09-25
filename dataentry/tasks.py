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
    from .utlis import send_email_notification,process_csv_cpu
    from notifications_app.models import BroadcastNotification

    # ==================== Step 0: Find model dynamically ====================
    model = None
    for app_config in apps.get_app_configs():
        try:
            model = apps.get_model(app_config.label, model_name)
            break
        except LookupError:
            continue
    if not model:
        raise ValueError(f"Model {model_name} not found in any installed app")

    # ==================== Step 1: New event loop ====================
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # ==================== Step 2: CPU-bound CSV processing using ProcessPoolExecutor ====================
    with ProcessPoolExecutor(max_workers=4) as executor:
        future = executor.submit(process_csv_cpu, file_path)
        processed_data = future.result()   # process_csv_cpu returns a list of dicts

    # ==================== Step 3: Save data to DB ====================
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
def export_data_task(model_name, user_email, user_id):
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from .utlis import async_write_csv, generate_csv_file, send_email_notification
    from notifications_app.models import BroadcastNotification
    from django.apps import apps

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    model = apps.get_model('dataentry', model_name)
    data = model.objects.all()
    data_list = [{field.name: getattr(row, field.name) for field in model._meta.fields} for row in data]

    file_path = generate_csv_file(model_name)
    fieldnames = [field.name for field in model._meta.fields]

    # Async CSV write
    loop.run_until_complete(async_write_csv(file_path, fieldnames, data_list))

    # Email send using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as pool:
        pool.submit(send_email_notification, 'Export Done', f'{model_name} export completed', [user_email], file_path)

    # Broadcast Notification
    BroadcastNotification.objects.create(
        user_id=user_id,
        message=f"{model_name} data export completed successfully"
    )
