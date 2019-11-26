from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-task/', views.create_task, name='create-task'),
    path('settings/', views.settings, name='settings'),
    path('detail/tk<int:task_id>/', views.detail, name='detail'),
    path('upload/', views.sceneImgUpload, name='uploadimg'),
    path('upload/&responseType=json', views.sceneImgUpload),
    path('taskchat/', views.taskchat, name='chat-urls'),
]
