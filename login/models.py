# login/models.py

from django.db import models
from django.conf import settings


class User(models.Model):
    '''用户表'''

    gender = (
        ('male','男'),
        ('female','女'),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    stu_id = models.CharField(max_length=13, unique=True)
    phone = models.CharField(max_length=11, unique=True, default='None')
    dept = models.CharField(max_length=50, default='None')
    money = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)
    send_state = models.IntegerField(default=1)
    updated_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'

class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"


class OrderInfo(models.Model):
    '''
    充值订单详情
    '''
    ORDER_STATUS = (
        ('TRADE_SUCCESS', '交易支付成功'),
        ('TRADE_CLOSED', '未付款交易超时关闭'),
        ('WAIT_BUYER_PAY', '交易创建'),
        ('TRADE_FINISHED', '交易结束'),
        ('PAYING', '待支付'),
    )
    username = models.CharField(max_length=128, default='None')
    order_sn = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name='订单号')
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付订单号')

    pay_status = models.CharField(choices=ORDER_STATUS, max_length=40, verbose_name='订单状态', default='paying')
    order_mount = models.DecimalField(verbose_name="充值金额", max_digits=10,
                                decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-order_sn']
        verbose_name = "充值订单"
        verbose_name_plural = '充值订单'

    def __str__(self):
        return self.order_sn