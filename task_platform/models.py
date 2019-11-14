from django.db import models

# Create your models here.
class Task(models.Model):
    '''任务'''
    state = (
        ('not_stared', '未开始'),
        ('processing', '进行中'),
        ('abort', '中止'),
        ('revoke', '撤销'),
        ('timeout', '超时'),
        ('completed', '完成')
    )

    publisher = models.CharField(max_length=128)
    receiver = models.CharField(max_length=128)
    deadline = models.DateTimeField('deadline')
    pub_time = models.DateTimeField(auto_now_add=True)
    task_detail = models.CharField(max_length=300)
    task_state = models.CharField(max_length=32, choices=state, default='未开始')

    def __str__(self):
        return self.task_detail
    
    class Meta:
        ordering = ['pub_time']
        verbose_name = '任务'
        verbose_name_plural = '任务'
