from django.urls import path
from django.views.generic import TemplateView
from .views import JobDescriptionAPI, AnalyzeResumeAPI

urlpatterns = [
  
    path("", TemplateView.as_view(template_name="resumechecker/resumecheckers.html"), name="resume_home"),

    # APIs
    path("api/jobdescriptions/", JobDescriptionAPI.as_view(), name="job_descriptions"),
    path("api/analyze-resume/", AnalyzeResumeAPI.as_view(), name="analyze_resume"),
]
