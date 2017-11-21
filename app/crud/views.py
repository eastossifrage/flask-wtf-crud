# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from flask import render_template, redirect, request, current_app, url_for, flash, json
from . import crud
from ..models import User
from .forms import AddUserForm, DeleteUserForm, EditUserForm
from ..import db
from threading import Lock
from app import socketio
from flask_socketio import emit


thread = None
thread_lock = Lock()


def background_thread(users_to_json):
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(5)

        socketio.emit('user_response', {'data': users_to_json}, namespace='/websocket/user_refresh')


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
        return redirect(url_for('.websocket'))

    return render_template('edit_websocket.html', editUserForm=edit_user_form, user=user)


@socketio.on('connect', namespace='/websocket/user_refresh')
def connect():
    global thread
    with thread_lock:
        users = User.query.all()
        users_to_json = [user.to_json() for user in users]

        if thread is None:
            thread = socketio.start_background_task(background_thread, (users_to_json, ))
    emit('server_response', {'data': '试图连接客户端！'})


@socketio.on('connect_event', namespace='/websocket/user_refresh')
def refresh_message(message):

    emit('server_response', {'data': message['data']})
