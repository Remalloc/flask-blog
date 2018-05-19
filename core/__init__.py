# -*- coding: utf-8 -*-
import os

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# 创建一个Flask的实例
app = Flask(__name__)
bcrypt = Bcrypt(app)  # bcrypt加密模块

# 默认配置
app.config['ROOT_PATH'] = os.path.dirname(__file__)  # 根目录
app.config['SECRET_KEY'] = "*J2F0Fz&Q(A(Sb$8oygTHcwWRjp4poL&"  # Session密钥
app.config['ADMIN_UID'] = 1  # 管理员id号
app.config['TIME_ZONE'] = 'Asia/Shanghai'  # 时区

# 配置 Flask_SQLalchemy
app.config['SQLALCHEMY_DATABASE_PATH'] = os.path.join(app.config['ROOT_PATH'], 'blog.db')  # 数据库位置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['SQLALCHEMY_DATABASE_PATH']  # 连接数据库地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁止追踪修改对象

# 实例化数据库
db = SQLAlchemy(app)

# 导入其他模块,必须在配置完成后导入
import core.modle
import core.page
