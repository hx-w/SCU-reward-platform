from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-task/', views.create_task, name='create-task'),
    path('settings/', views.settings, name='settings'),
    path('detail/tk<int:task_id>/', views.detail, name='detail')
]
