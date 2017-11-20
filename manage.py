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
manager.add_command('run', socketio.run(app=app, host='0.0.0.0', port=5001))


if __name__ == '__main__':
    manager.run()
