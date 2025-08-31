from django.urls import path
from . import views  # Import your app's views

urlpatterns = [
    path('', views.index, name='index'),  
    path('contact/', views.contact, name='contact'), 
    path('about/', views.about, name='about'), 
    path('Terms-and-Condition/', views.Terms_and_Condition, name='Terms-and-Condition'), 
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'), 
   

]