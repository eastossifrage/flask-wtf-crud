

# 基于 flask + socket.io 的 CRUD 异步操作

> Flask 作为一个全栈架构，如果你只会 python，而不懂 javascript 的前端知识，似乎是无法支撑起你的 web 梦想的，比如，一个简单的页面 **局部刷新** 功能，你就需要用到 ajax 的知识，当然，你还可以使用 HTML5 的新特性 —— websocket功能，好在 flask 还提供了一个 flask-socketio 插件，本文我们就探讨一下这个 flask-scoketio插件的用法。

## 理解 websocket 协议

 - **HTTP 协议只能通过客户端发起请求来与客户端进行通讯** —— 这是一个缺陷。
 - **通过websocket 协议，服务器可以主动向客户端推送信息，客户端也可以主动向服务器发送信息，是真正的双向平等对话，属于服务器推送技术的一种。**
 
### websocket 协议特性

1. 建立在 TCP 协议之上，服务器端的实现比较容易。
2. 与 HTTP 协议有着良好的兼容性。默认端口也是80和443，并且握手阶段采用 HTTP 协议，因此握手时不容易屏蔽，能通过各种 HTTP 代理服务器。
3. 数据格式比较轻量，性能开销小，通信高效。
4. 可以发送文本，也可以发送二进制数据。
5. 没有同源限制，客户端可以与任意服务器通信。
6. 协议标识符是ws（如果加密，则为wss），服务器网址就是 URL。

## 使用 flask-socketio

### 安装插件

```
pip install flask-socketio
```

### 项目结构

本文是在[ 《基于 flask 的 CRUD 操作》 ](http://www.os373.cn/article/95)的基础上增加了 webscoket 的功能，使用的是 `init_app()` 的形式加载 flask-socketio 插件，和*网上的大多数教程稍有不同*。

```
flask-wtf-crud/
|-- env/
	|-- <python虚拟环境>
|-- app/ <项目的模块名称>
	|-- crud/ <前端蓝图>
		|-- __init__.py
		|-- views.py <路由和视图函数文件>
		|-- forms.py <表单类文件, wtforms插件必须项>
		|-- templates <HTML模板>
		    |-- static <静态文件夹>
		        |-- js <JavaScript 文件夹>
		            |-- crud.js # 异步请求的程序主要在此添加
	|-- XXXXXX/ <其它蓝图>
	|-- __init__.py
	|-- models.py <数据库模型文件>
|-- migrations/ <数据库表关系文件夹,Flask-Migrate迁移数据库时使用>
|-- config.py <项目的配置文件>
|-- manage.py <用于启动程序以及其它程序任务>
```

### 将 flask-socketio 引入项目

#### 修改 manage.py 内容

```python
# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

import os
from app import create_app, db, socketio
from app.models import User
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app=app)
migrate = Migrate(app=app, db=db)

def make_shell_context():
    return dict(app=app, db=db, User=User)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('run', socketio.run(app=app, host='0.0.0.0', port=5001)) # 新加入的内容


if __name__ == '__main__':
    manager.run()

```

####　修改 app/\_\_init\_\_.py 内容

```python
# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_socketio import SocketIO # 新加入的内容
db = SQLAlchemy()

async_mode = None
socketio = SocketIO()


def create_app(config_name):
    """ 使用工厂函数初始化程序实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app=app)

    db.init_app(app=app)

    socketio.init_app(app=app, async_mode=async_mode) # 新加入的内容

    # 注册蓝本crud
    from .crud import crud as crud_blueprint
    app.register_blueprint(crud_blueprint, url_prefix='/crud')

    return app
```

#### 当前蓝图的 views.py

```python
# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from flask import render_template, redirect, request, current_app, url_for, flash, json
from . import crud
from ..models import User
from .forms import AddUserForm, DeleteUserForm, EditUserForm
from ..import db
from threading import Lock
from app import socketio # 新加入的内容
from flask_socketio import emit # 新加入的内容

# 新加入的内容-开始
thread = None
thread_lock = Lock()

def background_thread(users_to_json):
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(5) \\ 每五秒发送一次

        socketio.emit('user_response', {'data': users_to_json}, namespace='/websocket/user_refresh')
# 新加入的内容-结束

@crud.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')


@crud.route('/websocket', methods=['GET', 'POST'])
def websocket():
    add_user_form = AddUserForm(prefix='add_user')
    delete_user_form = DeleteUserForm(prefix='delete_user')
    if add_user_form.validate_on_submit():
        if add_user_form.role.data == u'True':
            role = True
        else:
            role = False
        if add_user_form.status.data == u'True':
            status = True
        else:
            status = False
        u = User(username=add_user_form.username.data.strip(), email=add_user_form.email.data.strip(),
                 role=role, status=status)
        db.session.add(u)
        flash({'success': u'添加用户<%s>成功！' % add_user_form.username.data.strip()})
    if delete_user_form.validate_on_submit():
        u = User.query.get_or_404(int(delete_user_form.user_id.data.strip()))
        db.session.delete(u)
        flash({'success': u'删除用户<%s>成功！' % u.username})

    users = User.query.all()

    return render_template('websocket.html', users=users, addUserForm=add_user_form, deleteUserForm=delete_user_form)


@crud.route('/websocket-edit/<user_id>', methods=['GET', 'POST'])
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    edit_user_form = EditUserForm(prefix='edit_user', obj=user)
    if edit_user_form.validate_on_submit():
        user.username = edit_user_form.username.data.strip()
        user.email = edit_user_form.email.data.strip()
        if edit_user_form.role.data == u'True':
            user.role = True
        else:
            user.role = False
        if edit_user_form.status.data == u'True':
            user.status = True
        else:
            user.status = False
        flash({'success': u'用户资料已修改成功！'})
        return redirect(url_for('.basic'))

    return render_template('edit_websocket.html', editUserForm=edit_user_form, user=user)

# 新加入的内容-开始
@socketio.on('connect', namespace='/websocket/user_refresh')
def connect():
    """ 服务端自动发送通信请求 """
    global thread
    with thread_lock:
        users = User.query.all()
        users_to_json = [user.to_json() for user in users]

        if thread is None:
            thread = socketio.start_background_task(background_thread, (users_to_json, ))
    emit('server_response', {'data': '试图连接客户端！'})


@socketio.on('connect_event', namespace='/websocket/user_refresh')
def refresh_message(message):
    """ 服务端接受客户端发送的通信请求 """

    emit('server_response', {'data': message['data']})
# 新加入的内容-结束
```


---------- **以上内容是后端的内容，以下内容是将是前段的内容** ----------

#### crud.js 内容

```javascript
$(document).ready(function () {
    namespace='/websocket/user_refresh';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    $("#url_show").text("websocket URL: " + location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() { // 发送到服务器的通信内容
        socket.emit('connect_event', {data: '我已连接上服务端！'});
    });

    socket.on('server_response', function(msg) {
        \\ 显示接受到的通信内容，包括服务器端直接发送的内容和反馈给客户端的内容
        $('#log').append('<br>' + $('<div/>').text('接收 : ' + msg.data).html());
    });
    socket.on('user_response', function(msg) {
        //console.log(eval(msg.data[0]));
        //$('#users_show').append('<br>' + $('<div/>').text('接收 : ' + msg.data).html());
        var tbody = "";
        var obj = eval(msg.data[0]);
        $.each(obj, function (n, value) {
            var role = "";
            if (value.role===true){
                role = "管理员";
            }else {
                role = "一般用户";
            }
            var status = "";
            if (value.status===true){
                status = "正常";
            }else {
                status = "注销";
            }
            edit_url = "<a href=" +  location.protocol + '//' + document.domain + ':' + location.port + "/crud/websocket-edit/" + value.id + "> 修改</a>";
            delete_url = "<a href=\"javascript:delete_user_" + value.id + "()\">删除</a>";
            var trs = "";
            trs += "<tr><th>" + (n+1) + "</th><td>" + value.username + "</td><td>" + value.email + "</td><td>" + role + "</td><td>" + status + "</td><td>" + edit_url + " | " + delete_url +"</td></tr>";
            tbody += trs;
        })
        $('#users_show').empty();
        $('#users_show').append(tbody);
    });
});
```

## 显示结果

![](http://www.os373.cn/admin/pictures/flask_crud/004.png)

每次打开网页，会显示服务端发送的内容——“试图连接客户端！”，其后，客户端返回给服务端——“我已连接上服务端！”，而后又被服务端返回给客户端显示。

以下的表格内容显示数据局里的内容，每 5 秒局部刷新一次表格内容。

服务器后端 log 日志内容如下：

![](http://www.os373.cn/admin/pictures/flask_crud/005.png)

## 总结

 1. 由于 flask 架构具有上下文的限制，在数据库里 **增加删改** 内容的时候，表格的内容没有变化——尽管局部已经进行了刷新。要想显示变化后的数据库内容，必须得重新启动一下 flask 服务。
 2. 就整体的部署来说，在 flask 项目里添加 websocket 协议，显得项目较重，实现一个局部刷新的功能还是用 ajax 比较简单。
 3. 欢迎大侠能够给我的项目提出修改意见，先行感谢！！！

## 参考

 - [基于 flask 的 CRUD 操作](http://www.os373.cn/article/95)
 - [WebSocket 教程 —— 阮一峰](http://www.ruanyifeng.com/blog/2017/05/websocket.html?utm_source=tuicool&utm_medium=referral)

