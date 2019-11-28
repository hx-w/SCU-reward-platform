# -*- coding: utf-8 -*-
import time
import os
import hashlib
from decimal import Decimal
from pathlib import Path
from django.shortcuts import render, get_object_or_404, redirect, Http404, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Task, Task_tags, User_task
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


def settings(request):
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
        settings(request)
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
    sort_choice_list = (
        '发布时间 最近', '发布时间 最远',
        '报价 最低', '报价 最高'
    )
    is_publisher = True
    if username != publisher:
        publisher = 'xxx'
        is_publisher = False
    message = ''
    user_task_list = User_task.objects.filter(task_id=task_id)
    if request.method == 'GET':
        accept_id = request.GET.get('accept', None)
        if accept_id:
            user_task_acc = User_task.objects.get(id=accept_id)
            task_acc = Task.objects.get(id=user_task_acc.task_id)
            task_acc.receiver = user_task_acc.username
            task_acc.task_state = '进行中'
            task_acc.save()
            return redirect('/')

    if request.method == 'POST':
        if 'settings' in request.POST:
            settings(request)
        else:
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
            user_task = User_task.objects.create(task_id=task_id)
            user_task.username = username
            user_task.description = description
            # user_task.submit_money = Decimal.from_float(float(money))
            user_task.submit_money = float(money)
            user_task.save()
    
    return render(request, 'task_platform/detail.html', locals())


def create_task(request):
    '''
    - task_description   - expected_time_consuming
    - task_detail        - tag_list
    - people_needed
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
            settings(request)
        else:
            # 返回该任务详细信息页 /detail/tk Id
            task_description = request.POST.get('task_description')
            task_detail = request.POST.get('task_detail')
            people_needed = request.POST.get('people_needed')
            expected_time_consuming = request.POST.get('expected_time_consuming')
            tag_list = request.POST.get('tag_list')
            tags = tag_list.split(' ')
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
    latest_task_list = Task.objects.filter(publisher=username).order_by('-pub_time')
    for task in latest_task_list:
        color = 'tt-color0{} tt-badge'.format(finder[task.task_state]) 
        tag_list.append(
            (task, color,
             Task_tags.objects.filter(task_id=task.id).order_by('sig_tag')))
    return render(request, 'task_platform/profile.html', locals())

def taskchat(request):
    
    return render(request, 'task_platform/taskchat.html', locals())

