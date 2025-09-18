from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import JobDescriptionSerializer, ResumeSerializer
from .models import JobDescription,Resume
from .analyzer import process_resume

class JobDescriptionAPI(APIView):
    def get(self , request):
        queryset = JobDescription.objects.all()
        serializer = JobDescriptionSerializer(queryset, many = True)
        return Response({
            'status' : True,
            'data' : serializer.data
        })