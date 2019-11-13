from django.contrib import admin

# Register your models here.

# login/admin.py

from django.contrib import admin
from . import models

admin.site.register(models.User)
