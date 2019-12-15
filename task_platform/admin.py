from django.contrib import admin
from . import models

admin.site.register(models.Task)
admin.site.register(models.Task_tags)
admin.site.register(models.User_task)
admin.site.register(models.Task_receive)
admin.site.register(models.Chatinfo)
admin.site.register(models.ChatVision)
admin.site.register(models.Withdraw)