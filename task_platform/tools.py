# -*- coding: utf-8 -*-
import time
import os
import hashlib
from decimal import Decimal
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from .models import Withdraw, ChatVision
os.path.abspath('../')
from login.models import User

@csrf_exempt
def hash_code(s, salt='hx+ltq+wzy+hxj'):  # 加点盐
    h = hashlib.sha256()
    h.update((s + salt).encode())  # update方法只接收bytes类型
    return h.hexdigest()

@csrf_exempt
def get_room_id(task):
    md5 = hashlib.md5()
    md5.update('{}{}'.format(task.id, task.publisher).encode())
    return md5.hexdigest()

@csrf_exempt
def get_notice_room_id(username):
    md5 = hashlib.md5()
    md5.update(username.encode())
    return md5.hexdigest()

@csrf_exempt
def send_notice(username, message):
    notice = Chatinfo.objects.create(room_id=get_notice_room_id(username))
    notice.sender = 'Admin'
    notice.message = message
    notice.save()
    flag = ChatVision.objects.create(room_id=get_notice_room_id(username))
    flag.username = username
    flag.has_seen = False
    flag.save()

'''
这个函数是在测试中使用
通过后台创建的账号没有聊天框，可以通过这个函数生成，不过最好别用
'''
@csrf_exempt
def check_chatroom_exist():
    alluser = User.objects.all()
    for euser in alluser:
        send_notice(euser.name, '创建账号成功，开启你的赏金之旅吧！')
    alltask = Task.objects.all()
    for task in alltask:
        new_info = Chatinfo.objects.create(task_id=task.id)
        new_info.room_id = get_room_id(task)
        new_info.sender = 'Admin'
        new_info.save()
        if task.task_state == '进行中':
            send_notice(task.publisher, '恭喜你，任务已经开始，请关心任务动态！')
            for allrec in Task_receive.objects.filter(task_id=task.id):
                send_notice(allrec.username, '恭喜你，任务已经开始，请关心任务动态！')


def chatinfo_num(username):
    # 检查提现更新
    withs = Withdraw.objects.filter(username=username, state='完成', noticed=False)
    for each_with in withs:
        send_notice(username, '恭喜您，您于{}发起的提现{}元的请求已经接受，请查看您支付宝余额，如果有问题请联系platform_office@163.com。'.format(each_with.start_time.strftime('%Y-%m-%d %M:%H:%S'), each_with.money))
        each_with.noticed = True
        each_with.save()

    chatnum = ChatVision.objects.filter(username=username, has_seen=False).count()
    return chatnum

def self_settings(request, user):
    # POST
    message_ = '格式错误'
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    new_dept = request.POST.get('new_dept', '')
    new_phone = request.POST.get('new_phone', '')
    #-------
    flg_changed = False
    if new_password1 != new_password2:
        return '两次输入的密码不同！'

    if new_phone.strip() != '':
        same_phone = User.objects.filter(phone=new_phone)
        if same_phone:
            return '手机号码已被注册，请重新输入！'
        new_phone = new_phone.strip()
        if new_phone.isdigit() == False or len(new_phone) != 11:
            return '手机号码有误，请重新输入！'
        user.phone = new_phone
        flg_changed = True

    if new_dept.strip() != '':
        new_dept = new_dept.strip()
        if len(new_dept) > 50:
            return '学院名过长，请重新输入！'
        user.dept = new_dept
        flg_changed = True

    if flg_changed:
        user.save()
        message_ = ''
    return '修改成功'

def check_deposit(username, money, swicth_=True):
    # makesure username in User
    user = User.objects.get(name=username)
    if money > user.money:
        return False
    else:
        if swicth_:
            user.money -= Decimal.from_float(money)
            user.save()
        return True