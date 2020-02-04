import json
import time
from dwebsocket.decorators import accept_websocket,require_websocket
from django.shortcuts import render
from django.db.models import Q
from .models import ChatMess

@accept_websocket
def test_websocket(request):

    if request.is_websocket(): # 如果请求是websocket请求：

        WebSocket = request.websocket
        username = request.session.get('user_name', None)
        messages = {}

        while True:
            time.sleep(0.7) # 休眠1秒

            # 判断是否通过websocket接收到数据
            if WebSocket.has_messages():

                # 存在Websocket客户端发送过来的消息
                try:
                    client_msg = WebSocket.read().decode('utf-8')
                    # 设置发送前端的数据
                    messages = {
                        'time': time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())),
                        'sender': username,
                        'msg': client_msg,
                    }
                    ChatMess.objects.create(sender=username, message=client_msg)
                    request.websocket.send(json.dumps(messages))
                except:
                    pass
            else:
                # 设置发送前端的数据
                new_message = ChatMess.objects.filter(~Q(sender=username), sended=False).order_by('send_time').first()
                # new_message = ChatMess.objects.filter(sended=False).exclude(sender=username).order_by('send_time').first()
                if new_message:
                    new_message.sended = True
                    new_message.save()
                    messages = {
                        'time': new_message.send_time.strftime('%Y.%m.%d %H:%M:%S'),
                        'sender': new_message.sender,
                        'msg': new_message.message,
                    }
                    # 设置发送数据为json格式
                    request.websocket.send(json.dumps(messages))


def test_websocket_client(request):
    return render(request,'TEST/websocket_client.html')
