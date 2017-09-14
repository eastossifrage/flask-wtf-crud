# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from flask import render_template, redirect, request, current_app, url_for, flash
from . import crud
from ..models import User
from .forms import AddUserForm, DeleteUserForm, EditUserForm
from ..import db


@crud.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')


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


