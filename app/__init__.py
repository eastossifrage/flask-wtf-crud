# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = u'http://www.os373.cn'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_socketio import SocketIO
db = SQLAlchemy()

async_mode = None
socketio = SocketIO()


def create_app(config_name):
    """ 使用工厂函数初始化程序实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app=app)

    db.init_app(app=app)

    socketio.init_app(app=app, async_mode=async_mode)

    # 注册蓝本crud
    from .crud import crud as crud_blueprint
    app.register_blueprint(crud_blueprint, url_prefix='/crud')

    return app
