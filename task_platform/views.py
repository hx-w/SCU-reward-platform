# -*- coding: utf-8 -*-
import time
import os
import hashlib
import random
from decimal import Decimal
from pathlib import Path
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect, Http404, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings
from .models import Task, Task_tags, User_task, Task_receive
os.path.abspath('../')
from login.models import User

# Create your views here.

@csrf_exempt
def hash_code(s, salt='hx+ltq+wzy+hxj'):  # 加点盐
    h = hashlib.sha256()
    h.update((s + salt).encode())  # update方法只接收bytes类型
    return h.hexdigest()


@csrf_exempt
def sceneImgUpload(request):
    username = request.session.get('user_name')
    if request.method == 'POST':
        try:
            path = 'media/upload/' + time.strftime("%Y/%m/%d/",
                                                   time.localtime())
            dirpath = Path(path)
            dirpath.mkdir(parents=True, exist_ok=True)

            f = request.FILES["upload"]
            file_name = path + '_' + username + '_' + str(
                time.time()) + '_' + f.name
            des_origin_f = open(file_name, "wb+")
            for chunk in f.chunks():
                des_origin_f.write(chunk)
            des_origin_f.close()
        except Exception as e:
            print(e)
        res = {
            'uploaded': True,
            'url': '/' + file_name,
        }
        return JsonResponse(res)
    else:
        raise Http404()


def self_settings(request):
    username = request.session.get('user_name', None)
    user = User.objects.get(name=username)
    # POST
    message = '格式错误'
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    new_dept = request.POST.get('new_dept', '')
    new_phone = request.POST.get('new_phone', '')
    #-------
    flg_changed = False
    if new_password1 != new_password2:
        message = '两次输入的密码不同！'
        return 

    if new_phone.strip() != '':
        same_phone = User.objects.filter(phone=new_phone)
        if same_phone:
            message = '手机号码已被注册，请重新输入！'
            return 
        new_phone = new_phone.strip()
        if new_phone.isdigit() == False or len(new_phone) != 11:
            message = '手机号码有误，请重新输入！'
            return 
        user.phone = new_phone
        flg_changed = True

    if new_dept.strip() != '':
        new_dept = new_dept.strip()
        if len(new_dept) > 50:
            message = '学院名过长，请重新输入！'
            return
        user.dept = new_dept
        flg_changed = True

    if flg_changed:
        user.save()
        message = ''
    return

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

def index(request):
    # latest_task_list = Task.objects.order_by('-pub_time')[:10]
    username = request.session.get('user_name', None)
    tag_list = []
    if username:
        user = User.objects.get(name=username)
        student_id = user.stu_id
        phone = user.phone
        dept = user.dept
        if user.dept == 'None':
            dept = '暂无信息'

    finder = {
        '未开始': '9', '进行中': '2',
        '中止': '3', '撤销': '3', 
        '超时': '3', '完成': '4'
    }
    latest_task_list = Task.objects.order_by('-pub_time')
    for task in latest_task_list:
        color = 'tt-color0{} tt-badge'.format(finder[task.task_state]) 

        tag_list.append(
            (task, color,
             Task_tags.objects.filter(task_id=task.id).order_by('sig_tag')))

    if request.method == 'POST':
        '''
        处理settings:
        student_id, phone, dept
        new_password1, new_password2, new_dept, new_phone
        message
        '''
        self_settings(request)
    return render(request, 'task_platform/index.html', locals())

def detail(request, task_id):
    '''
    GET:
        publisher, pub_time, task_description, tag_list
        task_detail, user_task_list, is_publisher
    POST:
        money, description
    '''
    
    username = request.session.get('user_name', None)
    if not username:
        return redirect('/login/')
    user = User.objects.get(name=username)
    student_id = user.stu_id
    phone = user.phone
    dept = user.dept
    if user.dept == 'None':
        dept = '暂无信息'
    
    task = get_object_or_404(Task, pk=task_id)
    tag_list = Task_tags.objects.filter(task_id=task.id)
    publisher = task.publisher
    pub_time = task.pub_time
    task_description = task.task_description
    task_detail = task.task_detail
    task_state = task.task_state
    task_class = task.task_class


    sort_choice_list = (
        '发布时间 最近', '发布时间 最远',
        '报价 最低', '报价 最高'
    )
    is_publisher = True
    if username != publisher:
        publisher = '匿名用户：{}'.format(
            random.choice(('金刚鹦鹉', '小牛', '小鹿', '北极熊', '天辉', '夜魇'))
        )
        is_publisher = False
    message = ''
    user_task_list = User_task.objects.filter(task_id=task_id)
    percentage = settings.PERCENTAGE
    # 当前用户是否是接受者的一部分
    is_receiver = False
    try:
        Task_receive.objects.get(task_id=task.id, username=username)
        is_receiver = True
    except:
        is_receiver = False

    # 判断超时
    def is_overtime(task):
        return (
            task.task_state == '进行中'
            and timezone.now() > task.begin_time + timedelta(
                0, # 天
                float(task.expected_time_consuming) * 3600 # 秒
            )
        )


    if request.method == 'POST':
        if 'settings' in request.POST: # 个人信息修改
            self_settings(request)
        elif 'accept' in request.POST: # 发布者接受报价
            message = '任务已开始！'
            rec_list = request.POST.getlist('accept')
            if len(rec_list) > task.people_needed:
                message = '接受的报价过多！'
                return render(request, 'task_platform/detail.html', locals())
            elif len(rec_list) == 0:
                message = '请选择至少一项报价！'
                return render(request, 'task_platform/detail.html', locals())
            else:
                # 支付逻辑实现 and 未接受报价回退
                rec_list = list(rec[:-1] for rec in rec_list)
                rec_money = dict(zip(rec_list, map(lambda rec: user_task_list.get(username=rec).submit_money, rec_list)))
                if user.money < sum(rec_money.values()):
                    redirect('/recharge/')
                if task_class == '赏金模式':
                    for money_ in rec_money.values():
                        check_deposit(publisher, float(money_) * (1 + percentage))
                        exl_money_qs = user_task_list.exclude(username__in=rec_list).values_list('username', 'submit_money')
                        exl_money = dict(exl_money_qs)
                    for rec, money_ in exl_money.items():
                        check_deposit(rec, -float(money_))

                # 设置task
                task.begin_time = timezone.now()
                task.task_state = '进行中'
                task.save()
                # 设置接受
                for rec, money_ in rec_money.items():
                    task_rec = Task_receive.objects.create(task_id=task.id)
                    task_rec.username = rec
                    task_rec.done_money = money_
                    task_rec.save()

                return redirect('/profile/')
        elif 'submit_money_' in request.POST:   # 用户提交报价
            message = '提交成功'
            if publisher == username:
                message = '任务发布者无法提交报价'
                return render(request, 'task_platform/detail.html', locals())
            try:
                temp = User_task.objects.get(task_id=task_id, username=username)
                message = '您已经提交过报价，请勿重复提交！'
                return render(request, 'task_platform/detail.html', locals())
            except:
                pass
            
            description = request.POST.get('description')
            money = request.POST.get('money')
            if not check_deposit(username, float(money)):
                return redirect('/recharge/') # 余额不足
            user_task = User_task.objects.create(task_id=task_id)
            user_task.username = username
            user_task.description = description
            # user_task.submit_money = Decimal.from_float(float(money))
            user_task.submit_money = float(money)
            user_task.save()
            task.people_now += 1
            task.save()
        elif 'revoke_btn' in request.POST: # 发布者撤销
            '''
            - 发布者押金不退, 平均值退给接受者
            - 发布者支付金额全退
            - 接受者押金全退
            '''
            task_rec = Task_receive.objects.filter(task_id=task.id)
            tot_money, avg_deposit = 0.0, settings.DEPOSIT / task_rec.count() 
            for rec in task_rec:
                tot_money += float(rec.done_money)
                check_deposit(rec.username, -(float(rec.done_money) + avg_deposit)) # 回退接收者
            check_deposit(username, -float(tot_money * (1 + percentage))) # 回退发布者
            task.task_state = '撤销'
            task.end_time = timezone.now()
            task.save()
            return redirect('/profile/')
        elif 'abort_btn' in request.POST or is_overtime(task): # 接受者 中止
            '''
            - 发布者支付金额全退
            - 接受者押金不退，退给发布者
            - 所有接受者中止，任务结束, 发布者押金回退
            '''
            sig_rec = Task_receive.objects.filter(task_id=task.id)
            if task_class == '赏金模式':
                sig_rec = sig_rec.get(username=username)
                sig_rec.is_abort = True
                sig_rec.save()
                check_deposit(task.publisher, -float(sig_rec.done_money) * (1 + percentage)) # 回退发布者
                check_deposit(task.publisher, -float(sig_rec.done_money)) # 回退发布者
                task_rec = Task_receive.objects.filter(task_id=task.id)
                if not False in task_rec.values_list('is_abort'):
                    # 任务全部终止
                    check_deposit(task.publisher, -float(settings.DEPOSIT)) # 回退押金
                    task.task_state = '中止'
                    task.end_time = timezone.now()
                    task.save()
            elif task_class == '猎人模式':
                # 退给接受者发布者的押金，发布者支出回退
                sig_rec = sig_rec.first()
                check_deposit(sig_rec.username, -float(settings.DEPOSIT)-float(sig_rec.done_money))
                task.task_state = '中止'
                task.end_time = timezone.now()
                task.save()

            return redirect('/profile/')
        elif 'complete_btn' in request.POST:
            '''
            - 发布者押金回退
            - 接受者押金回退，接受者赏金
            '''
            task_rec = Task_receive.objects.filter(task_id=task.id)
            check_deposit(task.publisher, -settings.DEPOSIT) # 回退押金
            if task_class == '赏金模式':
                for rec in task_rec:
                    check_deposit(rec.username, -2 * float(rec.done_money))
            elif task_class == '猎人模式':
                task_rec = task_rec.first()
                check_deposit(task.publisher, -float(task_rec.done_money) * (1 - percentage))
            task.task_state = '完成'
            task.end_time = timezone.now()
            task.save()
            return redirect('/profile/')

    return render(request, 'task_platform/detail.html', locals())


def create_task(request):
    '''
    - task_description   - expected_time_consuming
    - task_detail        - tag_list
    - people_needed
    '''
    DEPOSIT = settings.DEPOSIT
    username = request.session.get('user_name', None)
    if not username:
        return redirect('/login/')
    user = User.objects.get(name=username)
    student_id = user.stu_id
    phone = user.phone
    dept = user.dept
    if user.dept == 'None':
        dept = '暂无信息'
    tag_list = []
    finder = {
        '未开始': '9', '进行中': '2',
        '中止': '3', '撤销': '3', 
        '超时': '3', '完成': '4'
    }
    latest_task_list = Task.objects.order_by('-pub_time')
    for task in latest_task_list:
        color = 'tt-color0{} tt-badge'.format(finder[task.task_state]) 
        tag_list.append(
            (task, color,
             Task_tags.objects.filter(task_id=task.id).order_by('sig_tag')))

    if request.method == "POST":
        if 'settings' in request.POST:
            self_settings(request)
        else:
            # 判断金额是否充足
            if not check_deposit(username, float(settings.DEPOSIT)):
                return redirect('/recharge/') # 余额不足
            # 返回该任务详细信息页 /detail/tk Id
            task_class = request.POST.get('v')
            task_description = request.POST.get('task_description')
            task_detail = request.POST.get('task_detail')
            people_needed = request.POST.get('people_needed')
            expected_time_consuming = request.POST.get('expected_time_consuming')
            tag_list = request.POST.get('tag_list')
            tags = tag_list.strip().split(' ')
            message = '任务创建成功'
            for tag in tags:
                if len(tag) > 20:
                    message = '标签：内容过长'
                    return render(request, 'task_platform/create-task.html', locals())
            if len(task_description) > 50 or len(task_description) == 0:
                message = '任务简述：无内容或内容过长！'
                return render(request, 'task_platform/create-task.html', locals())
            if len(task_detail) > 3000 or len(task_detail) == 0:
                message = '任务详情：无内容或内容过长！'
                return render(request, 'task_platform/create-task.html', locals())
            if not people_needed.isdigit():
                message = '所需人数：请输入数字'
                return render(request, 'task_platform/create-task.html', locals())
            if int(people_needed) > 50:
                message = '所需人数：数字过大'
                return render(request, 'task_platform/create-task.html', locals())
            # 没有检查 expected_time_consuming
            task = Task.objects.create()
            task.task_class = task_class
            task.publisher = username
            task.task_description = task_description
            task.task_detail = task_detail
            task.people_needed = people_needed
            task.expected_time_consuming = Decimal(expected_time_consuming)
            task.save()
            for tag in tags:
                tag_task = Task_tags.objects.create()
                tag_task.sig_tag = tag
                tag_task.task_id = task.id
                tag_task.save()
            return redirect('/')
    return render(request, 'task_platform/create-task.html', locals())


def profile(request):
    '''
    GET:
        money
    '''
    username = request.session.get('user_name', None)
    if not username:
        # 未登录用户无法访问 profile
        return redirect('/login/')
    user = User.objects.get(name=username)
    student_id = user.stu_id
    phone = user.phone
    dept = user.dept
    if user.dept == 'None':
        dept = '暂无信息'
    money = user.money   
    task_list_list = []
    if username:
        user = User.objects.get(name=username)
        student_id = user.stu_id
        phone = user.phone
        dept = user.dept
        if user.dept == 'None':
            dept = '暂无信息'
    # 颜色信息
    stcolor_finder = {
        '未开始': '9', '进行中': '2',
        '中止': '3', '撤销': '3', 
        '超时': '6', '完成': '4',
        '赏金模式': '5', '猎人模式': '7'
    }
    rec_task_id_list = []
    try:
        rec_task_id_list = Task_receive.objects.filter(username=username).values_list('task_id')
    except:
        pass
    latest_task_list = Task.objects.filter(
        Q(publisher=username) | Q(id__in=rec_task_id_list)
    ).order_by('-pub_time')

    tab_class = [
        ("task_class='赏金模式'", "_task.task_state"),
        ("task_class='猎人模式'", "_task.task_state"),
        ("task_state='未开始'", "_task.task_class"),
        ("task_state='进行中'", "_task.task_class"),
        ("Q(task_state='撤销')|Q(task_state='中止')|Q(task_state='超时')|Q(task_state='完成')",
        "_task.task_class")
    ]

    def calc_settlement(task, username):
        _settlement = '暂无'
        rec_task_list = Task_receive.objects.filter(task_id=task.id)
        if task.publisher == username:
            if task.task_class == '赏金模式':
                tot_money = 0
                for rec in rec_task_list:
                    if rec.is_abort:
                        tot_money -= float(rec.done_money) * (2 + settings.PERCENTAGE)
                    else:
                        tot_money += float(rec.done_money) * (1 + settings.PERCENTAGE)
                if task.task_state == '完成':
                    _settlement = -tot_money
                elif task.task_state in ['中止', '超时']:
                    _settlement = -tot_money
                elif task.task_state == '撤销':
                    
                    pass
            else:
                if task.task_state == '完成':
                    pass
                elif task.task_state in ['中止', '超时']:
                    pass
                elif task.task_state == '撤销':
                    pass
        elif username in rec_task_id_list.values_list('username'):
            if task.task_class == '赏金模式':
                if task.task_state == '完成':
                    pass
                elif task.task_state in ['中止', '超时']:
                    pass
                elif task.task_state == '撤销':
                    pass
            else:
                if task.task_state == '完成':
                    pass
                elif task.task_state in ['中止', '超时']:
                    pass
                elif task.task_state == '撤销':
                    pass
            pass
        return _settlement


    for idx in range(5):
        tag_list = []
        for _task in eval('latest_task_list.filter({})'.format(tab_class[idx][0])):
            _color = 'tt-color0{} tt-badge'.format(stcolor_finder[eval(tab_class[idx][1])])
            _settlement = '暂无'
            if _task.task_state in ["超时", "撤销", "中止", "完成"]:
                _settlement = '+1.12'
            tag_list.append(
                (_task, _color, _settlement,
                Task_tags.objects.filter(task_id=_task.id).order_by('sig_tag'))
            )
        task_list_list.append(tag_list)

    tag_list_1, tag_list_2, tag_list_3, tag_list_4, tag_list_5 = (
        task_list_list[0], task_list_list[1], task_list_list[2],
        task_list_list[3], task_list_list[4]
    )

    if request.method == 'POST' and 'settings' in request.POST:
        self_settings(request)
    return render(request, 'task_platform/profile.html', locals())

def taskchat(request):
    
    return render(request, 'task_platform/taskchat.html', locals())

