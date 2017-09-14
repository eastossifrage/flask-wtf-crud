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

