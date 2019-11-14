from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/tk<int:task_id>/', views.detail, name='detail')
]
