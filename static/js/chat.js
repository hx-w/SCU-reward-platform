var ws, myid;
window.onload = function () {
  //先判断浏览器是否支持websocket
  if ("WebSocket" in window) {
    // 打开一个 web socket,链接服务器
    ws = new WebSocket("ws://" + window.location.host + "/chat/");
    ws.onopen = function () {
      // Web Socket 已连接上，使用 send() 方法尝试发送数据
      ws.send("ws_conn_check");
    };
    //监听服务端是否有消息发送过来，当有消息时执行方法
    ws.onmessage = function (evt) {
      //获取服务器发来的消息
      var received_msg = evt.data;
      //判断是返回的是消息还是用户列表和id，1是消息，0是用户列表和id
      msg = eval("(" + received_msg + ")")
      //用户列表和id
      if (msg.type == 0) {
        //userid为空表示更新用户列表,不需要更新自己的id，否则为初次登录
        if (msg.userid != null) {
          myid = msg.userid
          $("#userid").append(myid)
        }
        //当收到新的用户列表时，清空原来的用户列表,清空原来的用户选择框,添加群组发送选项
        $("#userlist").empty()
        for (var i = 0; i < msg.userlist.length; i++) {
          //填充用户列表
          $("#userlist").append(msg.userlist[i] + "<hr />")
          //填充用户选择框
        }
      }
      //用户发送的消息
      else {
        var myDate = new Date();
        nowtime = myDate.toLocaleString(); //获取日期与时间
        newmsg = ""
        //判断是自己的消息，绿色显示
        if (myid == msg.data.user) {
          newmsg = "<span style='color:blue'>" + msg.data.user + ":" + nowtime + "<br />" + msg.data.msg + "</span>" + "<br />"
        } else {
          newmsg = "<span >" + msg.data.user + ":" + nowtime + "<br />" + msg.data.msg + "</span>" + "<br />"
        }
        $("#historymsg").append(
          newmsg
        )
      }
    };
    //关闭页面或其他行为导致与服务器断开链接是执行
    ws.onclose = function () {
      // 关闭 websocket
      alert("连接已关闭...");
    };
  } else {
    // 浏览器不支持 WebSocket
    alert("您的浏览器不支持 WebSocket!");
  }
}
//消息发送
function send() {
  // msgtxt = $("#msg").val();
  var msgtxt = CKEDITOR.instances.msg.getData();
  if (typeof msgtxt == "undefined" || msgtxt == null || msgtxt == "") return
  msg = {
    txt: msgtxt,
    userfrom: myid
  }
  //发送消息后清空消息框，并定位到消息框内
  $.post("/msg_send/", msg, function () {
    var editor = CKEDITOR.instances.msg;
    // 将光标移至最末
    editor.focus();
    editor.setData('');
  })
}