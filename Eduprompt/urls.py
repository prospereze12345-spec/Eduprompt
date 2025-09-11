from django.urls import path
from . import views  # Import your app's views

urlpatterns = [
    path('', views.index, name='index'),  
    path('contact/', views.contact, name='contact'), 
    path('about/', views.about, name='about'), 
    path('Terms_and_Condition/', views.Terms_and_Condition, name='Terms_and_Condition'), 
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'), 
    path("website/", views.website, name="website"),
    path("send-message", views.send_message, name="send_message"),
    path("flyer-design/", views.flyer_design, name="flyer_design"),
    path('contact-ajax/', views.contact_ajax, name='contact_ajax'),




   

]