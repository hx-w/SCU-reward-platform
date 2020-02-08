from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from chatroom import views


urlpatterns = [
    # ex:/assetinfo/test_websocket
    path('to_chat/', views.to_chat),
    path('chat/', views.chat),
    path('msg_send/', views.msg_send),
]