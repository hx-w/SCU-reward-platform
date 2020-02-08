import json
import time
from dwebsocket.decorators import accept_websocket,require_websocket
from django.shortcuts import render, HttpResponse
from django.db.models import Q
from .models import ChatMess
from django.views.decorators.csrf import csrf_exempt
import uuid

clients = {}

#聊天界面
def to_chat(request):
    return render(request, 'TEST/chat.html')

# 服务器方法，允许接受ws请求
@accept_websocket
def chat(request):
    # 判断是不是ws请求
    if request.is_websocket():
        # 保存客户端的ws对象，以便给客户端发送消息,每个客户端分配一个唯一标识
        userid=str(uuid.uuid1())[:8]
        clients[userid] = request.websocket
        print('uuid: ', userid)
        # 判断是否有客户端发来消息，若有则进行处理，表示客户端与服务器建立链接成功
        while True:
            '''获取消息，线程会阻塞，
            他会等待客户端发来下一条消息,直到关闭后才会返回，当关闭时返回None'''
            message=request.websocket.wait()
            if not message:
                break
            else:
                msg=str(message, encoding = "utf-8")
                print(msg)
                #1、发来test表示链接成功
                if msg == "test":
                    print("客户端链接成功："+userid)
                    #第一次进入，返回在线列表和他的id
                    request.websocket.send(json.dumps({"type":0,"userlist":list(clients.keys()),"userid":userid}).encode("'utf-8'"))
                    #更新所有人的userlist
                    for client in clients:
                        clients[client].send(json.dumps({"type":0,"userlist":list(clients.keys()),"user":None}).encode("'utf-8'"))
    #客户端关闭后从列表删除
    if userid in clients:
        del clients[userid]
        print(userid + "离线")
        # 更新所有人的userlist
        for client in clients:
            clients[client].send(
                json.dumps({"type": 0, "userlist": list(clients.keys()), "user": None}).encode("'utf-8'"))


#消息发送方法
@csrf_exempt
def msg_send(request):
    msg = request.POST.get("txt")
    useridto = request.POST.get("userto")
    useridfrom = request.POST.get("userfrom")
    type=request.POST.get("type")
    #发来{type:"2",msg:data,user:user},表示发送聊天信息，user为空表示群组消息，不为空表示要发送至的用户
    if type == "1":
        #群发
        for client in clients:
            clients[client].send(json.dumps({"type": 1, "data": {"msg": msg, "user": useridfrom}}).encode('utf-8'))
    else:
        # 私聊，对方显示
        clients[useridto].send(json.dumps({"type": 1, "data": {"msg": msg, "user": useridfrom}}).encode('utf-8'))
        # 私聊，自己显示
        clients[useridfrom].send(json.dumps({"type": 1, "data": {"msg": msg, "user": useridfrom}}).encode('utf-8'))
    return HttpResponse(json.dumps({"msg":"success"}))

