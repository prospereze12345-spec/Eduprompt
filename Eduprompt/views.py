from django.shortcuts import render
from django.conf import settings




# Create your views here.
def index(request):
    return render(request, 'index.html', {
        'AFRICAN_LANGUAGES': settings.AFRICAN_LANGUAGES
    })


def contact(request):
    return render(request, 'contact.html', {
        'AFRICAN_LANGUAGES': settings.AFRICAN_LANGUAGES
    })


def about(request):
    return render(request, 'about.html', {
        'AFRICAN_LANGUAGES': settings.AFRICAN_LANGUAGES
    })


def Terms_and_Condition(request):
    return render(request, 'Terms_and_Condition.html' ,{
        'AFRICAN_LANGUAGES': settings.AFRICAN_LANGUAGES
    })


def privacy_policy(request):
    return render(request, 'privacy_policy.html',
 {
        'AFRICAN_LANGUAGES': settings.AFRICAN_LANGUAGES
    })


