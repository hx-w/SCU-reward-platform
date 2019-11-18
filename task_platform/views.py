from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from django.views.decorators.csrf import csrf_exempt
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
    if username:
        user = User.objects.get(name=username)
        student_id = user.stu_id
        phone = user.phone
        dept = user.dept
        if user.dept == 'None':
            dept = '暂无信息'

    latest_task_list = Task.objects.order_by('-pub_time')

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
    username = request.session.get('user_name', None)
    if not username:
        return redirect('/login/')
    if request.method == "POST":
        # 返回该任务详细信息页 /detail/
        pass

    return render(request, 'task_platform/create-task.html', locals())

def settings(request):
    return render(request, 'task_platform/page-single_settings.html', locals())
    