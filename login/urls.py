# mysite_login/urls.py

from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from login import views

urlpatterns = [ 
    path('login/', views.login),
    path('register/', views.register),
    path('page-login/', views.page_login),
    path('page-signup/', views.page_signup),
    path('logout/', views.logout),
    path('confirm/', views.user_confirm),
    path('recharge/', views.recharge),
    path('alipay/pay/', views.alipay_pay),
    path('alipay/return/', views.alipay_return)
]