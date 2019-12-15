from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone

# Create your models here.


class Task_tags(models.Model):
    sig_tag = models.CharField(max_length=20, default="None")
    task_id = models.IntegerField(default="0")

    def __str__(self):
        return self.sig_tag

    class Meta:
        verbose_name = "任务标签"
        verbose_name_plural = "任务标签"


class Task_receive(models.Model):
    task_id = models.IntegerField(default="0")
    username = models.CharField(max_length=128, default="None")
    done_money = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_abort = models.BooleanField(default=False)
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "用户任务接受"
        verbose_name_plural = "用户任务接受"

class User_task(models.Model):
    task_id = models.IntegerField(default="0")
    username = models.CharField(max_length=128, default="None")
    description = models.CharField(max_length=50)
    submit_money = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    pub_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['pub_time']
        verbose_name = "用户任务报价"
        verbose_name_plural = "用户任务报价"

class Withdraw(models.Model):
    choice_ = (('发起', 'start'), ('完成', 'complete'), ('取消', 'cancel'))
    username = models.CharField(max_length=128, null=True, blank=True)
    img_path = models.CharField(max_length=256, null=True, blank=True)
    money = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    state = models.CharField(max_length=20, choices=choice_, null=True, blank=True)
    noticed = models.BooleanField(default=False)
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = '提现记录'
        verbose_name_plural = '提现记录'


class Chatinfo(models.Model):
    room_id = models.CharField(max_length=32, null=True, blank=True)
    task_id = models.IntegerField(null=True, blank=True)
    message = RichTextUploadingField(null=True, blank=True)
    sender = models.CharField(max_length=128, null=True, blank=True)
    send_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_id
    
    class Meta:
        ordering = ['send_time']
        verbose_name = '聊天信息'
        verbose_name_plural = '聊天信息'

class ChatVision(models.Model):
    room_id = models.CharField(max_length=32, null=True, blank=True)
    username = models.CharField(max_length=128)
    has_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    class Meta:
        ordering = ['has_seen']
        verbose_name = '消息查看'
        verbose_name_plural = '消息查看'


class Task(models.Model):
    '''任务'''
    state = (('未开始', 'waitting'), ('进行中', 'processing'), ('中止', 'abort'),
             ('撤销', 'revoke'), ('超时', 'timeout'), ('完成', 'completed'))
    publisher = models.CharField(max_length=128)
    pub_time = models.DateTimeField(auto_now_add=True)
    begin_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    people_needed = models.IntegerField(default=1)
    people_now = models.IntegerField(default=0)
    expected_time_consuming = models.DecimalField(
        max_digits=12, decimal_places=1, default=0.0)
    task_description = models.CharField(max_length=50, default="None")
    task_detail = RichTextUploadingField(default='None')
    task_state = models.CharField(max_length=32, choices=state, default='未开始')
    task_class = models.CharField(max_length=48, default='赏金模式')

    def __str__(self):
        return self.task_description

    class Meta:
        ordering = ['pub_time']
        verbose_name = '任务'
        verbose_name_plural = '任务'
