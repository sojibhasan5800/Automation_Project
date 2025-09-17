from django.shortcuts import redirect, render
from django.http import HttpResponse
from dataentry.tasks import import_data_task
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth

def home(request):
    return render(request, 'home.html')

def celery_test(request):
    # I want to execute a time consuming task here
    import_data_task.delay()
    return HttpResponse('<h3>Function executed successfully</h3>')







