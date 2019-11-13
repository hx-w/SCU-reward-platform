# mysite_login/urls.py

from django.conf.urls import url
from django.contrib import admin
from login import views

urlpatterns = [
    url('admin/', admin.site.urls),
    url('index/', views.index),
    url('login/', views.login),
    url('register/', views.register),
    url('logout/', views.logout),
]