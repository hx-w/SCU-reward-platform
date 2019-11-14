from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'task_platform/index.html')

def detail(request, task_id):
    return HttpResponse("你在浏览任务#%d的详细描述" % task_id)
    