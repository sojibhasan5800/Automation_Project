import os
from django.http import FileResponse, Http404
from django.shortcuts import render,redirect
from .utlis import generate_csv_file, get_all_custom_models,check_csv_errors
from uploads.models import Upload
from django.conf import settings
from django.contrib import messages
from django.core.management import call_command
from .tasks import import_data_task,export_data_task


# Create your views here.
def import_data(request):
    if request.method == 'POST':
        file_path = request.FILES.get('file_path')
        model_name = request.POST.get('model_name')
        user_email = request.user.email
        user_id = request.user.id
        
        # store this file inside the Upload model
        upload = Upload.objects.create(file=file_path, model_name=model_name)

        # construct the full path
        relative_path = str(upload.file.url)
        base_url = str(settings.BASE_DIR)
        file_path = base_url+relative_path

        # check for the csv errors
        try:
            check_csv_errors(file_path, model_name)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('import_data')
        
        # handle the import data task here
        import_data_task.delay(file_path, model_name,user_email,user_id)

        # show the message to the user
        messages.success(request, 'Your data is being imported, you will be notified Email when once it is done.')
        return redirect('import_data')
        

    else:
        custom_models = get_all_custom_models(True)
        context={
            'custom_models':custom_models
        }
        return render(request,'dataentry/importdata.html',context)



def export_data(request):
    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        user_email = request.user.email
        user_id = request.user.id

        # call the export data task
        export_data_task.delay(model_name,user_email,user_id)

        # show the message to the user
        messages.success(request, "Please check your email — the exported data file has been sent to you.")
        return redirect('export_data')
    else:
        custom_models = get_all_custom_models(True)
        context = {
            'custom_models': custom_models,
        }
    return render(request, 'dataentry/exportdata.html', context)