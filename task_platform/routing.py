# -*- coding: utf-8 -*-
from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/', ChatConsumer),
]