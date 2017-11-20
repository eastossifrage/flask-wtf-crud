# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import User


class AddUserForm(FlaskForm):
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


class DeleteUserForm(FlaskForm):
    user_id = StringField()


class EditUserForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64, message=u'姓名长度要在1和64之间'),
                       Regexp(ur'^[\u4E00-\u9FFF]+$', flags=0, message=u'用户名必须为中文')])
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    role = SelectField(u'权限', choices=[(u'True', u'管理员'), (u'False', u'一般用户') ])
    status = SelectField(u'状态', choices=[(u'True', u'正常'), (u'False', u'注销')])
    submit = SubmitField(u'修改用户')


