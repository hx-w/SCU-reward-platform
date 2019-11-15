from django import forms
from captcha.fields import CaptchaField


class UserForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        max_length=128, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="密码", 
        max_length=256, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    captcha = CaptchaField(
        label=''
       # widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class RegisterForm(forms.Form):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    username = forms.CharField(
        label="用户名",
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    student_id = forms.CharField(
        label="学号",
        max_length=13,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="密码(六位以上)", 
        max_length=256, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="确认密码", 
        max_length=256, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label="手机号码", 
        max_length=256, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="邮箱地址", 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    sex = forms.ChoiceField(
        label='性别', 
        choices=gender
    )
    captcha = CaptchaField(label='验证码')
