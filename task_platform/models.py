from django.db import models

# Create your models here.
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
    receiver = models.CharField(max_length=128)
    deadline = models.DateTimeField('deadline')
    pub_time = models.DateTimeField(auto_now_add=True)
    task_description = models.CharField(max_length=50, default="None")
    task_detail = models.CharField(max_length=300)
    task_state = models.CharField(max_length=32, choices=state, default='未开始')

    def __str__(self):
        return self.task_detail
    
    class Meta:
        ordering = ['pub_time']
        verbose_name = '任务'
        verbose_name_plural = '任务'
