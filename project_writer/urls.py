from django.urls import path
from . import views
from .views import download_project_pdf

urlpatterns =[
path("project-writer/", views.project_writer, name="project_writer"),    
path('generate-project/', views.generate_project, name='generate_project'),
path("download-pdf/", download_project_pdf, name="download_pdf"),

]