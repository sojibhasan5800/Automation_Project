from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import JobDescriptionSerializer, ResumeSerializer
from .models import JobDescription, Resume
from .analyzer import process_resume
from rest_framework.permissions import AllowAny



class JobDescriptionAPI(APIView):
    def get(self, request):
        queryset = JobDescription.objects.all()
        serializer = JobDescriptionSerializer(queryset, many=True)
        return Response({
            'status': True,
            'data': serializer.data
        })


class AnalyzeResumeAPI(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        try:
            data = request.data
            if not data.get('job_description'):
                return Response({
                    'status': False,
                    'message': 'job_description is required',
                    'data': {}
                })

            serializer = ResumeSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    'status': False,
                    'message': 'errors',
                    'data': serializer.errors
                })

            resume_instance = serializer.save()
            resume_path = resume_instance.resume.path

            job = JobDescription.objects.get(id=data.get('job_description'))
            analyzed_data = process_resume(resume_path, job.job_description)

            return Response({
                'status': True,
                'message': 'resume analyzed',
                'data': analyzed_data
            })
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e),
                'data': {}
            })
