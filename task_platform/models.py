from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField

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
