# 基于 flask 的 CRUD 操作

---

> 个人拙见，web 后端就是一个对数据库进行 CRUD （增删改查）的操作过程。
本章内容就是基于 flask 这个前后端一体化的架构，使用 flask-wtf 插件，打通前后端的联系，来讲解一下 CRUD 操作。

## 配置 flask 项目

参照 [你应该会玩儿 flask](http://www.os373.cn/tag/%E4%BD%A0%E5%BA%94%E8%AF%A5%E4%BC%9A%E7%8E%A9flask)的前几章教程，使用大型项目的结构即**蓝图模式**来配置项目。

项目结构如下：

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
	|-- XXXXXX/ <其它蓝图>
	|-- __init__.py
	|-- models.py <数据库模型文件>
|-- migrations/ <数据库表关系文件夹,Flask-Migrate迁移数据库时使用>
|-- config.py <项目的配置文件>
|-- manage.py <用于启动程序以及其它程序任务>
```

对于 crud 蓝图的配置，不再赘述，如果想了解，可以查看源码。


## 作品内容：

![](http://www.os373.cn/admin/pictures/flask_crud/001.png)
![](http://www.os373.cn/admin/pictures/flask_crud/002.png)


## 配置数据库示例

创建一个 User 数据库字段。

```python
# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from . import db


class User(db.Model):
    '''Example for crud
    以用户为例，来展示 CRUD 操作！
    '''
    __tablename__ = 'crud'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    status = db.Column(db.Boolean, default=False)
    role = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User %r>' % self.username
```

## 创建视图函数 views.py

```python
# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from flask import render_template, redirect, request, current_app, url_for, flash
from . import crud
from ..models import User
from .forms import AddUserForm, DeleteUserForm, EditUserForm
from ..import db

@crud.route('/basic', methods=['GET', 'POST'])
def basic():
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


    return render_template('basic.html', users=users, addUserForm=add_user_form,
                           deleteUserForm=delete_user_form)

@crud.route('/basic-edit/<user_id>', methods=['GET', 'POST'])
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


    return render_template('edit_basic.html', editUserForm=edit_user_form, user=user)

```

> 知识点：
1. 视图函数中实现了增加功能和删除功能。
2. 多个删除功能也只是需要一个 form 类表单来实现，主要的难点在于前端设计。
3. 实现了修改功能的视图函数，初看是一个简单的单 form 表单提交功能而已，但是，请记住这行代码`edit_user_form = EditUserForm(prefix='edit_user', obj=user)`，特别是`obj=user`，其中 user 是 User 数据库类的实例，这样的功能将实现修改功能的模板能够**显示出原有的实例的内容**。![](http://www.os373.cn/admin/pictures/flask_crud/003.png)


## 创建 forms.py 表单类

```python
# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from flask_wtf import Form
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import User


class AddUserForm(Form):
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64, message=u'姓名长度要在1和64之间'),
                       Regexp(ur'^[\u4E00-\u9FFF]+$', flags=0, message=u'用户名必须为中文')])
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    role = SelectField(u'权限', choices=[(u'True', u'管理员'), (u'False', u'一般用户') ])
    status = SelectField(u'状态', choices=[(u'True', u'正常'), (u'False', u'注销') ])
    submit = SubmitField(u'添加用户')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被注册！')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册！')


class DeleteUserForm(Form):
    user_id = StringField()


class EditUserForm(Form):
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64, message=u'姓名长度要在1和64之间'),
                       Regexp(ur'^[\u4E00-\u9FFF]+$', flags=0, message=u'用户名必须为中文')])
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    role = SelectField(u'权限', choices=[(u'True', u'管理员'), (u'False', u'一般用户') ])
    status = SelectField(u'状态', choices=[(u'True', u'正常'), (u'False', u'注销')])
    submit = SubmitField(u'修改用户')

```

>知识点：
1. 进行了表单的验证，查看 flask-wtf 官方文档即可。
2. 实现了用户名和邮箱的唯一性验证。**此处留一个彩蛋，在模板中，我没有实现唯一性的提示功能，你可以自己添加，欢迎留言。**

## 创建前段模板

### 首先创建 `basic.html` 加载 bootstrap 前端框架，不再赘述。

#### `basic.html` 模板内容

```html
{% extends 'common/base.html' %}<!-- 加载基础模板，主要是bootstrap 框架及一些个性化的静态文件-->
{% block content %}
{% include 'common/alert.html' %}<!-- 加载提示模板-->
<h3 class="page-header"> CRUD 基本示例</h3>
<table class ="table table-hover">
    <thead>
        <tr>
            <th>序号</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>权限</th>
            <th>状态</th>
            <th>
                <button type="button" class="btn btn-primary pull-right" data-toggle="modal" data-target=".bs-example-modal-sm">增加</button>
            </th>
        </tr>
    </thead>
    <tbody class="small">
        <tr>
            {% for user in users %}
                <tr>
                    <th scope="row">{{ loop.index }}</th>
                    <td>{{ user.username}}</td>
                    <td>{{ user.email}}</td>                    
                    {% if user.role %}
                        <td>管理员</td>
                    {% else %}
                        <td>一般用户</td>
                    {% endif %}
                    {% if user.status %}
                        <td>正常</td>
                    {% else %}
                        <td>注销</td>
                    {% endif %}
                    <td><a href="{{ url_for('.user_edit', user_id=user.id) }}"> 修改</a><!-- 修改功能需跳转到另外一个页面 --> |
                        <a href="javascript:delete_user_{{ user.id }}()">删除</a>
                        <form method="post" role="form" id="delete_user_{{ user.id }}"><!-- 实现了删除功能的 form-->
                            {{ deleteUserForm.hidden_tag() }}
                            {{ deleteUserForm.user_id(class="hidden", value=user.id) }}
                        </form><!-- 实现了删除功能的 form 结束-->
                        <script type="text/javascript">
                           function delete_user_{{ user.id }}(){
                               $("#delete_user_{{ user.id }}").submit() ;
                           }
                        </script><!-- 删除 功能用到一些 js 知识 和 jinja2 知识 -->
                    </td>
                </tr>
                {% endfor %}
        </tr>
    </tbody>
</table>    
<div class="modal fade bs-example-modal-sm" tabindex="-1" role="dialog" aria-labelledby="mySmallModalLabel">
    <div class="modal-dialog modal-sm" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="gridSystemModalLabel">增加信息</h4>
            </div>
            <div class="modal-body">
                <form method="post" role="form"><!-- 实现了增加功能的 form-->
                    {{ addUserForm.hidden_tag() }}                    
                    <div class="input-group">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-user"></i> </span>
                        {{ addUserForm.username(class="form-control", placeholder="用户名",required="", autofocus="") }}
                    </div>
                    <div class="input-group">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-envelope"></i> </span>
                        {{ addUserForm.email(class="form-control", placeholder="邮 箱", required="") }}
                    </div>
                    <div class="input-group">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-briefcase"></i> </span>
                        {{ addUserForm.role(class="form-control", required="") }}
                    </div>
                    <div class="input-group">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-tree-deciduous"></i> </span>
                        {{ addUserForm.status(class="form-control", required="") }}
                    </div>
                    <div class="modal-footer">
                        <input class="btn btn-default" type="reset" value="重 置">
                        {{ addUserForm.submit(class="btn btn-primary") }}
                    </div>
                </form><!-- 实现了增加功能的 form 结束-->
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

> **知识点**：
1. 一个页面里有多个 form，包括 modal 里实现的增加功能的 form 和 实现了删除功能的 form。
2. 实现了删除功能的 form 并不是单独的存在，二是通过 jinja2 的**循环功能**，生成了不同 id 的具有删除功能的 form。
3. 修改功能是通过另外一个单独的页面实现。

#### `edit_basic.html` 模板内容

```html
{% extends 'common/base.html' %}
{% block content %}
<div class="row">
    <div class="col-xs-12 col-sm-offset-2">
        <form method="post" role="form">
            {{ editUserForm.hidden_tag() }}
            <div class="col-xs-12 col-sm-8">              
                <div class="input-group">
                    <span class="input-group-addon"><i class="glyphicon glyphicon-user"></i> </span>
                    {{ editUserForm.username(class="form-control", placeholder="用户名",required="", autofocus="") }}
                </div>
                <div class="input-group">
                    <span class="input-group-addon"><i class="glyphicon glyphicon-envelope"></i> </span>
                    {{ editUserForm.email(class="form-control", placeholder="邮 箱", required="") }}
                </div>
                <div class="input-group">
                    <span class="input-group-addon"><i class="glyphicon glyphicon-briefcase"></i> </span>
                    {{ editUserForm.role(class="form-control", required="") }}
                </div>
                <div class="input-group">
                    <span class="input-group-addon"><i class="glyphicon glyphicon-tree-deciduous"></i> </span>
                    {{ editUserForm.status(class="form-control", required="") }}
                </div>
                <div class="modal-footer">
                    <input class="btn btn-default" type="reset" value="重 置">
                    {{ editUserForm.submit(class="btn btn-primary") }}
                </div>
            </div>
        </form>
    </div>
</div>


{% endblock %}
```

> 知识点： 无。参照 flask-wtf 的官方文档即可。
