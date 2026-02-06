"""
URL configuration for new_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
        # <-- provides set_language view
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('', include('Eduprompt.urls')), 
    path('', include('users.urls')),
    path('note/', include('note.urls')),
    path('essay/', include('essay.urls')),
    path('', include('quiz_generator.urls')),
    path('', include('ai_solver.urls')),
    path('', include('project_writer.urls')),
    path('', include('grammar_checker.urls')),
    path('accounts/', include('allauth.urls')),
    path('blog/', include('blog.urls', namespace='blog')), 
    


] 


    


   


