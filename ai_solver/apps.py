# ai_solver/apps.py
from django.apps import AppConfig

class MathSolverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_solver'

    def ready(self):
        import ai_solver.signals  
