from django.shortcuts import render, get_object_or_404, redirect
from .models import Task, Task_tags
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import os
os.path.abspath('../')
from login.models import User

# Create your views here.

@csrf_exempt
def hash_code(s, salt='hx+ltq+wzy+hxj'):# 加点盐
    h = hashlib.sha256()
    h.update((s + salt).encode())  # update方法只接收bytes类型
    return h.hexdigest()


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

    latest_task_list = Task.objects.order_by('-pub_time')
    for task in latest_task_list:
        tag_list.append((task, Task_tags.objects.filter(task_id=task.id).order_by('sig_tag')))
    
    if request.method == 'POST':
        '''
        处理settings:
        student_id, phone, dept
        new_password1, new_password2, new_dept, new_phone
        message
        '''
        message = '格式错误'
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')
        new_dept = request.POST.get('new_dept', '')
        new_phone = request.POST.get('new_phone', '')
        #-------
        flg_changed = False
        if new_password1 != new_password2:
            message = '两次输入的密码不同！'
            return render(request, 'task_platform/index.html', locals())
        
        if new_phone.strip() != '':
            same_phone = User.objects.filter(phone=new_phone)
            if same_phone:
                message = '手机号码已被注册，请重新输入！'
                return render(request, 'task_platform/index.html', locals())
            new_phone = new_phone.strip()
            if new_phone.isdigit() == False or len(new_phone) != 11:
                message = '手机号码有误，请重新输入！'
                return render(request, 'task_platform/index.html', locals())
            user.phone = new_phone
            flg_changed = True

        if new_dept.strip() != '':
            new_dept = new_dept.strip()
            if len(new_dept) > 50:
                message = '学院名过长，请重新输入！'
                return render(request, 'task_platform/index.html', locals())
            user.dept = new_dept
            flg_changed = True

        if flg_changed:
            user.save()
            message = ''
            return render(request, 'task_platform/index.html', locals())        
    
    return render(request, 'task_platform/index.html', locals())        
        

def detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    context = { 'task': task }
    return render(request, 'task_platform/detail.html', context)

def create_task(request):
    '''
    - task_description   - expected_time_consuming
    - task_detail        - tag_list
    - people_needed
    '''
    username = request.session.get('user_name', None)
    if not username:
        return redirect('/login/')
    tag_list = []
    latest_task_list = Task.objects.order_by('-pub_time')
    for task in latest_task_list:
        tag_list.append((task, Task_tags.objects.filter(task_id=task.id).order_by('sig_tag')))
    if request.method == "POST":
        # 返回该任务详细信息页 /detail/tk Id
        task_description = request.POST.get('task_description')
        task_detail = request.POST.get('task_detail')
        people_needed = request.POST.get('people_needed')
        expected_time_consuming = request.POST.get('expected_time_consuming')
        tag_list = request.POST.get('tag_list')
        task = Task.objects.create()
        task.publisher = username
        tags = tag_list.split(' ')
        message = '任务创建成功'
        for tag in tags:
            if len(tag) > 20:
                message = '标签：内容过长'
                return render(request, 'task_platform.html', locals())
        if len(task_description) > 50 or len(task_description) == 0:
            message = '任务简述：无内容或内容过长！'
            return render(request, 'task_platform.html', locals())
        if len(task_detail) > 300 or len(task_detail) == 0:
            message = '任务详情：无内容或内容过长！'
            return render(request, 'task_platform.html', locals())
        if not people_needed.isdigit():
            message = '所需人数：请输入数字'
            return render(request, 'task_platform.html', locals())
        if int(people_needed) > 50:
            message = '所需人数：数字过大'
            return render(request, 'task_platform.html', locals())
        # 没有检查 expected_time_consuming
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

def settings(request):
    return render(request, 'task_platform/page-single_settings.html', locals())
    