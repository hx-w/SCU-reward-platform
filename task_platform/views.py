from django.shortcuts import render, get_object_or_404
from .models import Task

# Create your views here.

def index(request):
    latest_task_list = Task.objects.order_by('-pub_time')[:10]
    context = { 'latest_task_list': latest_task_list }
    return render(request, 'task_platform/index.html', context)

def detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    context = { 'task': task }
    return render(request, 'task_platform/detail.html', context)
    