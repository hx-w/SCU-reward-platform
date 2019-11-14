from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('<int:task_id>/', views.detail, name='detail')
]
