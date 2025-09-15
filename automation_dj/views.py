from django.shortcuts import redirect, render
from django.http import HttpResponse
from dataentry.tasks import import_data_task
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth

def home(request):
    context = {}
    if request.user.is_authenticated:
        # Only generate room_name for authenticated users
        context['room_name'] = f"user_{request.user.id}" 

    return render(request, 'home.html',context)

def celery_test(request):
    # I want to execute a time consuming task here
    import_data_task.delay()
    return HttpResponse('<h3>Function executed successfully</h3>')







