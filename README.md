# SCU-reward-platform

利用Djiango和bootstrap进行开发的四川大学任务悬赏平台(网页)，也是数据库课程设计项目。

## 2019/11/13 [test]

> 环境配置

- Python 3.*
- django (version <= 2.1.8)
- django-simple-captcha (验证码功能)
- alipay-sdk-python (支付宝接口)
- django-ckeditor (富文本编辑器)
- pillow (缩略图)
- channels==2.1.7`pip install -U channels`
- channels_redis==2.3.3 `pip inatll -U channels`

`python -m django --version`判断是否安装成功

> 测试

1. 在SCU-reward-platform/目录下运行`python manage.py runserver`
2. 打开浏览器访问[http://127.0.0.1:8000/](http://127.0.0.1:8000/)查看本地服务器是否启动成功

>代办

- [x] 完成注册功能
- [x] CSS渲染成功
- [x] 登录功能完成
- [x] 增加管理员账号(Carol)
- [x] 增加基础数据库内容，SQLite(Django自带)
- [ ] 图片验证码点击更新
- [x] 主页设计

## 2019/11/14 [test]

>代办

- [x] 完成邮箱验证

## 2019/11/16 [test]

>代办

- [x] 完善注册学号验证逻辑
- [x] 注册/登录界面重构
- [x] 支付宝接口接入
- [x] 个人信息修改
- [ ] confirm.html界面重构

## 2019/11/18[test]

> 代办

- [x] 加入充值界面(简陋) /recharge/
- [ ] 加入创建任务界面 /create-task/
- [ ] 将主页导航栏加入base.html方便

## 2019/11/20[test]

- [x] 修复注册功能后端BUG
- [x] 添加富文本功能

## 2019/11/24[test]

- [x] 任务详情中新增图片上传功能