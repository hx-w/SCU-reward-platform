# -*- coding: utf-8 -*-
import time
import os
import re
import base64
import task_platform.models as models
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings
os.path.abspath('../')
import login.models as login_models


class Admin_Sender(object):
    def __init__(self):
        self.__funcStr = {
            1: ('帮助', '提现', '统计'),
            2: ('\d+(\.\d+)?', '取消'),
            3: ('<img src=.+? />'),
            4: ('取消'),
            5: ('确认')
        }
        self.__state = 1  # DFA

    def __str__(self):
        return '当前状态：{}'.format(self.__state)

    def __send_notice__(self, message, username, room_id):
        notice = models.Chatinfo.objects.create(
            room_id=room_id, sender='Admin', message=message)
        notice.save()
        flag = models.ChatVision.objects.create(
            room_id=room_id, username=username, has_seen=False)
        flag.save()

    def __state_1(self, message, username, room_id):
        if re.search(self.__funcStr[self.__state][0], message):
            self.__send_notice__(
                '目前我们提供两种操作：\n1. 回复 "提现"，可以进行赏金提现，最低5rmb\n2.回复 "统计"，查看你的网站使用数据统计。',
                username, room_id)
        elif re.search(self.__funcStr[self.__state][1], message):
            self.__user.send_state = 2
            self.__user.updated_time = timezone.now()
            self.__user.save()
            self.__send_notice__(
                '正在进行提现操作，请回复您所需提现的金额(纯数字)，最低5赏金，输入之后赏金将会自动从您的账户中扣除，并引导您发送收款码给管理员。',
                username, room_id)
        elif re.search(self.__funcStr[self.__state][2], message):
            self.__send_notice__(
                '该功能正在建设中...',
                username, room_id)
        else:
            self.__send_notice__('请输入 "帮助" 来查看我们提供的功能说明。', username, room_id)

    def __state_2(self, message, username, room_id):
        if re.search(self.__funcStr[self.__state][0], message):
            message = re.search(self.__funcStr[self.__state][0], message)
            # 输入的是纯数字
            if self.__user.money < float(message.group()):
                self.__send_notice__(
                    '您的账户余额为{}，不足{}，无法提现，请输入其他金额数目或回复"取消" 来取消当前操作。'.format(self.__user.money, message.group()),
                    username, room_id
                )
            elif float(message.group()) < 5:
                self.__send_notice__(
                    '提现最低金额为5赏金，请输入其他金额数目或回复"取消" 来取消当前操作',
                    username, room_id
                )
            else:
                _money = Decimal.from_float(float(message.group()))
                withdraw = models.Withdraw.objects.create(username=username, money=_money, state='发起')
                withdraw.save()
                self.__user.send_state = 3
                self.__user.updated_time = timezone.now()
                self.__user.save()    
                self.__send_notice__(
                    '已记录您需提现{}元，请上传您的支付宝永久收款码，多次上传以最后一次为准。',
                    username, room_id
                )   
        elif re.search(self.__funcStr[self.__state][1], message):
            self.__user.send_state = 1
            self.__user.updated_time = timezone.now()
            withdraw_list = models.Withdraw.objects.filter(username=username, state='发起')
            if withdraw_list:
                withdraw_list.order_by('-start_time').first().state = '取消'
                withdraw_list.save()
        else:
            self.__send_notice__(
                '请输入提现金额(纯数字)，最低5赏金，回复"取消" 来取消当前操作。',
                username, room_id)

    def __state_3(self, message, username, room_id):
        
        pass
    
    def recieve(self, message, username, room_id):
        self.__user = login_models.User.objects.get(name=username)
        self.__state = self.__user.send_state
        if self.__state == 1:
            self.__state_1(message, username, room_id)
        elif self.__state == 2:
            self.__state_2(message, username, room_id)
        elif self.__state ==3:
            self.__state_3(message, username, room_id)
