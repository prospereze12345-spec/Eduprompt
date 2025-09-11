from django.urls import path
from . import views
from .views import ai_solver

urlpatterns = [
    path("ai-solver/", views.ai_solver, name='ai_solver'),   # main page + API POST
    path("api/solve/", views.ai_solver, name="api_solver"), # AJAX POST (optional, reuse same view)
    path("solve-image/", views.solve_image_api, name='solve_image_api'),

    path('download-pdf/', views.download_solution_pdf, name='download_solution_pdf'),
]