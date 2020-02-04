
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from TEST import views


urlpatterns = [
    # ex:/assetinfo/test_websocket
    path('test_websocket', views.test_websocket , name='test_websocket'),
    path('test_websocket_client', views.test_websocket_client , name='test_websocket_client'),
]
