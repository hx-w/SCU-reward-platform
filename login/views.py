from django.shortcuts import render

# Create your views here.
# login/views.py

from django.shortcuts import render,redirect

def index(request):
    pass
    return render(request,'login/index.html')

def login(request):
    pass
    return render(request,'login/login.html')

def register(request):
    pass
    return render(request,'login/register.html')

def logout(request):
    pass
    return redirect('/index/')
    