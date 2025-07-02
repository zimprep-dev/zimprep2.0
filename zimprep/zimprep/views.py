from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

# from django.template import loader

def home(request):
    # template = loader.get_template('base.html')
    return render(request, 'landing/base.html')

def dashboard(request):
    return render(request, 'authed-user/dashboard.html')
def login(request):
    return render(request,'landing/login-page.html')

