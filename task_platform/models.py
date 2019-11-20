from django.db import models
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

class Task(models.Model):
    '''任务'''
    state = (
        ('未开始', 'waitting'),
        ('进行中', 'processing'),
        ('中止', 'abort'),
        ('撤销', 'revoke'),
        ('超时', 'timeout'),
        ('完成', 'completed')
    )

    publisher = models.CharField(max_length=128)
    receiver = models.CharField(max_length=128, default="", blank=True)
    pub_time = models.DateTimeField(auto_now_add=True)
    people_needed = models.IntegerField(default=1)
    people_now = models.IntegerField(default=0)
    expected_time_consuming = models.DecimalField(max_digits=12, decimal_places=1, default=0.0)
    task_description = RichTextUploadingField(default="None")
    task_detail = models.CharField(max_length=300)
    task_state = models.CharField(max_length=32, choices=state, default='未开始')

    def __str__(self):
        return self.task_description
    
    class Meta:
        ordering = ['pub_time']
        verbose_name = '任务'
        verbose_name_plural = '任务'
