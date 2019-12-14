# -*- coding: utf-8 -*-
# login/views.py

import hashlib
import datetime
import time
import random
import os
from decimal import *
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from .forms import UserForm, RegisterForm
from . import models
from .pay import AliPay
os.path.abspath('../')
from task_platform.models import Chatinfo


@csrf_exempt
def hash_code(s, salt='hx+ltq+wzy+hxj'):# 加点盐
    h = hashlib.sha256()
    h.update((s + salt).encode())  # update方法只接收bytes类型
    return h.hexdigest()

def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user,)
    return code

def send_email(email, code):
    
    from django.core.mail import EmailMultiAlternatives

    subject = '来自SCU-reward-platform的注册确认邮件'

    text_content = '''感谢注册SCU-reward-platform，这里是四川大学任务悬赏平台注册系统，\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>SCU-reward-platform</a></p>
                    <p>这里是四川大学任务悬赏平台注册系统</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def login(request):
    hashkey = CaptchaStore.generate_key()
    imgage_url = captcha_image_url(hashkey)
    if request.session.get('is_login',None):
         return redirect('/')

    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        login_form = UserForm(request.POST)
        message = "请检查填写的内容, " + username + "!"
        if login_form.is_valid():
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = '请前往您的邮箱'+user.stu_id +'@stu.scu.edu.cn 进行确认！'
                    return render(request, 'login/login.html', locals())
                if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    # 发送通知
                    
                    return redirect('/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户"+ username + "不存在" 
            return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())

def page_login(request):
    hashkey = CaptchaStore.generate_key()
    imgage_url = captcha_image_url(hashkey)
    if request.session.get('is_login',None):
         return redirect('/')

    if request.method == "POST":
        # username = request.POST.get('username', '')
        # password = request.POST.get('password', '')
        login_form = UserForm(request.POST)
        message = "请检查填写的傻逼内容！fuck"
        if login_form.is_valid():
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = '用户还未经过邮件确认！'
                    return render(request, 'login/page-login.html', locals())
                if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户"+ username +"不存在" 
            return render(request, 'login/page-login.html', locals())
    login_form = UserForm()
    return render(request, 'login/page-login.html', locals())

def register(request):
    hashkey = CaptchaStore.generate_key()
    imgage_url = captcha_image_url(hashkey)
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get('username', '')
        student_id = request.POST.get('student_id', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        phone = request.POST.get('phone', '')
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容, "+username+"!"
        if register_form.is_valid():  # 获取数据
            message = "验证码对了， 但是请检查填写的内容！"
            email = student_id + '@stu.scu.edu.cn' # SCU邮箱
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user and list(same_name_user)[0].has_confirmed:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                elif same_name_user and list(same_name_user)[0].has_confirmed == False:
                    same_name_user.delete()
                same_stu_id = models.User.objects.filter(stu_id=student_id)
                if same_stu_id and list(same_stu_id)[0].has_confirmed:   # 学号唯一
                    message = '学生邮箱已被注册，请重新输入邮箱！'
                    return render(request, 'login/register.html', locals())
                elif same_stu_id and list(same_stu_id)[0].has_confirmed == False:
                    same_stu_id.delete()
                same_phone = models.User.objects.filter(phone=phone)
                if same_phone and list(same_phone)[0].has_confirmed:   # 学号唯一
                    message = '手机号码已被注册，请重新输入手机号码！'
                    return render(request, 'login/register.html', locals())
                elif same_phone and list(same_phone)[0].has_confirmed == False:
                    same_phone.delete()
                # 当一切都OK的情况下，创建新用户
                
                new_user = models.User.objects.create()
                new_user.name = username
                new_user.stu_id = student_id
                new_user.password = hash_code(password1)  # 使用加密密码
                new_user.phone = phone
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)
                message = '请前往邮箱确认！'
                return render(request, 'login/confirm.html') # 跳转确认页面
                # return redirect('/login/')  # 自动跳转到登录页面
        else:
            message = '可能是验证码填写错误！'        
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())

def page_signup(request):
    hashkey = CaptchaStore.generate_key()
    imgage_url = captcha_image_url(hashkey)
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get('username', '')
        student_id = request.POST.get('student_id', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        phone = request.POST.get('phone', '')
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容, "+username+"!"
        if register_form.is_valid():  # 获取数据
            message = "验证码对了， 但是请检查填写的内容！"
            email = student_id + '@stu.scu.edu.cn' # SCU邮箱
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/page-signup.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/page-signup.html', locals())
                same_stu_id = models.User.objects.filter(stu_id=student_id)
                if same_stu_id:   # 学号唯一
                    message = '学生邮箱已被注册，请重新输入邮箱！'
                    return render(request, 'login/page-signup.html', locals())
                same_phone = models.User.objects.filter(phone=phone)
                if same_phone:   # 学号唯一
                    message = '手机号码已被注册，请重新输入学号！'
                    return render(request, 'login/page-signup.html', locals())
                # 当一切都OK的情况下，创建新用户
                new_user = models.User.objects.create()
                new_user.name = username
                new_user.stu_id = student_id
                new_user.password = hash_code(password1)  # 使用加密密码
                new_user.phone = phone
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)
                message = '请前往邮箱确认！'
                return render(request, 'login/confirm.html') # 跳转确认页面
        else:
            message = 'something went wrong!'        
    register_form = RegisterForm()
    return render(request, 'login/page-signup.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/")

def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = timezone.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())

def recharge(request):
    if not request.session.get('user_name', None):
        return render(request, 'login/login.html', locals())
    return render(request, 'login/recharge.html', locals())

def alipay_pay(request):
    if not request.session.get('user_name', None):
        return redirect('/login/')
    alipayview = AlipayView()
    alipay = alipayview.dispatch(request)
    money = float(request.POST.get('money'))
    trade_no = str(time.time() + random.randint(0, 100))
    query_params = alipay.direct_pay(
        subject='四川大学任务悬赏平台<赏金币充值>',
        out_trade_no=trade_no,
        total_amount=money,
    )
    pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
    username = request.session.get('user_name', None)
    models.OrderInfo.objects.create(order_sn=trade_no, username=username)

    return redirect(pay_url)

def alipay_return(request):
    alipayview = AlipayView()
    alipay = alipayview.dispatch(request)
    if request.method == 'POST':
        alipayview.post(request)
    else:
        alipayview.get(request)
    return redirect('/')


class AlipayView(object):
    """
    支付宝支付
    get方法实现支付宝return_url，如果没有实现也无所谓，post同样可以更新状态
    post方法实现支付宝notify_url，异步更新

    支付宝返回的url如下：
    #http://127.0.0.1:8000/alipay/return/?
    # charset=utf-8&
    # out_trade_no=201902923423436&
    # method=alipay.trade.page.pay.return&
    # total_amount=1.00&
    # sign=CDBMY9NBsp4KICdQoBEVxGWobd0N8y4%2BU09stzUWwlNtLr7ZpELJdM5js20wXv%2FCPp0FGPbRW1YS9DRx0CnKJULZZMqysBUMH2FL39sS0Fgstgy1ydTs7ySXdHziJV0inI%2BDWAsebQqtjk5gQEweUstc%2B%2BnzjdgAulpvWzfJsbknS%2BqUfktSdF2ZOWGhr1CFlfsMFEDS2nzQv4K3E%2BNaeylkzUnRe9M1sjIL%2FYR0wVZ5A3OfHLPf9HzC2B8%2FLu4g7N5Vctkqp2aerDvIkN5SNmDnRGyjOt2b%2BOsLMqG4X06JSsrZT6Ln8PimsrkSOIGbj0gCqscx7BwZfmCQePlCw%3D%3D&
    # trade_no=2019082622001426981000041778&
    # auth_app_id=2016092600597838&
    # version=1.0&app_id=2016092600597838&
    # sign_type=RSA2&
    # seller_id=2088102177296610&
    # timestamp=2019-08-26+13%3A51%3A01
    """
    def dispatch(self, request, *args, **kwargs):
        self.alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.APP_NOTIFY_URL,
            app_private_key_path=settings.APP_PRIVATE_KEY_PATH,
            alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,
            debug=settings.ALIPAY_DEBUG,
            return_url=settings.RETURN_URL
        )
        #处理返回的url参数
        return self.alipay
        # return super(AlipayView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        """处理支付宝return_url返回"""
        callback_data = {}
        for key, value in request.GET.items():
            callback_data[key] = value
        sign = callback_data.pop('sign', None)
        self.order_sn = callback_data.get('out_trade_no', None) #订单号
        self.trade_no = callback_data.get('trade_no', None) #支付宝订单号
        self.order_mount = Decimal(callback_data.get('total_amount', None)) # 

        # 验证签名
        self.verify = self.alipay.verify(callback_data, sign)
        if self.verify:
            self.deposit()
            #返回个人中心页面
        return redirect('/') # 返回主页

    def post(self, request):
        """
        处理notify_url
        """
        callback_data = {}
        for key, value in request.GET.items():
            callback_data[key] = value
        sign = callback_data.pop('sign', None)
        self.order_sn = callback_data.get('out_trade_no', None) #订单号
        self.trade_no = callback_data.get('trade_no', None) #支付宝订单号
        self.order_mount = float(callback_data.get('total_amount', None)) # 
        self.order.save()
        # 验证签名
        self.verify = self.alipay.verify(callback_data, sign)
        if self.verify:
            self.deposit()
        return redirect('/')

    def deposit(self):
        """充值操作

        1.更新用户的金币信息
        2.更新订单状态为交易成功
        """
        def convert_rmb_to_money(rmb):
            return float(rmb) * settings.EXCHANGE_RATE
        # 数据库中查询订单记录
        order = models.OrderInfo.objects.get(order_sn=self.order_sn)
        # order = models.OrderInfo.objects.get(order_sn=self.order_sn)
        order.trade_no = self.trade_no

        # 把人民币转换成对应的金币
        rmb = self.order_mount
        money = convert_rmb_to_money(rmb)
        # 更新用户的金币
        user = models.User.objects.get(name=order.username)
        user.money = user.money + Decimal.from_float(money)
        user.save()
        # 订单状态置为交易成功
        order.pay_status = 'TRADE_SUCCESS'
        order.save()