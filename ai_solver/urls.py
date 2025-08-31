from django.urls import path
from . import views
from .views import ai_solver

urlpatterns =[
    path("ai-solver/", views.ai_solver, name="ai_solver"),
    path("api/solve/", ai_solver, name="api_solver"),
    path('download-pdf/', views.download_solution_pdf, name='download_solution_pdf'),
    path('solve-image/', views.solve_image_api,name='solve_image_api'),
]