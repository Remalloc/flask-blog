import json
from functools import wraps

from flask import render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, InputRequired, Length, EqualTo

from core import app
from core import sql


class RegisterForm(FlaskForm):
    # 注册表单
    # 数据验证错误时返回的错误信息:{'错误字段':['错误信息']}
    username = StringField('username', validators=[DataRequired(message="无效的用户名"),
                                                   Length(max=15, message="用户名不得超过15个字符")])
    password = PasswordField('password',
                             validators=[
                                 InputRequired(message="输入为空"),
                                 Length(min=6, max=20, message="密码限制在6~20个字符"),
                                 EqualTo("repeat_password", "两次输入的密码不相同")])
    repeat_password = PasswordField('repeat_password')
    email = StringField('email', validators=[Email(message="邮箱格式不符"), Length(max=30, message="邮箱不得超过30个字符")])


class LoginForm(FlaskForm):
    # 登录表单
    # 数据验证错误时返回的错误信息:{'错误字段':['错误信息']}
    username = StringField('username', validators=[DataRequired(message="无效的用户名"),
                                                   Length(max=15, message="用户名不得超过15个字符")])
    password = PasswordField('password',
                             validators=[
                                 InputRequired(message="输入为空"),
                                 Length(min=6, max=20, message="密码限制在6~20个字符")])


class CommentForm(FlaskForm):
    # 评论表单
    content = StringField('content', validators=[InputRequired(message="评论为空"),
                                                 Length(min=3, max=1000, message="评论字符数必须在3~1000个以内")])
    reply = StringField('reply')


def verify_email(form, field):
    # 邮箱验证函数,用于wtforms.validators中调用
    if field.data:
        Email(message="邮箱格式不符")(form, field)
        Length(max=30, message="邮箱不得超过30个字符")(form, field)


def verify_password(form, field):
    # 密码验证函数,用于wtforms.validators中调用
    if field.data:
        Length(min=6, max=20, message="密码限制在6~20个字符")(form, field)


class UserSettingForm(FlaskForm):
    # 个人设置表单
    origin_password = PasswordField('origin_password',
                                    validators=[InputRequired(message="原密码为空"),
                                                Length(min=6, max=20, message="密码限制在6~20个字符")])
    new_password = PasswordField('new_password',
                                 validators=[verify_password])
    email = StringField('email', validators=[verify_email])


def check_login(func):
    # @check_login 装饰器,通过session['logged_in']检查是否已经登录
    # 如未登录返回一个错误网页
    @wraps(func)
    def inner(*args, **kwargs):
        if session.get('logged_in', None):
            return func(*args, **kwargs)
        else:
            return "用户未登录"

    return inner


def check_admin(func):
    # @check_admin 装饰器,检查是否为管理员
    # 如未登录返回一个错误网页
    @wraps(func)
    def inner(*args, **kwargs):
        if session.get('uid', None) == app.config['ADMIN_UID']:
            return func(*args, **kwargs)
        else:
            return "禁止访问"

    return inner


@app.route('/')
def index():
    # 返回首页
    return render_template('index.html', home_active=True)


@app.route('/article')
def article():
    # 返回文章列表,需要提供page(分页参数),如果有aid(文章id号)则表示访问单个文章
    # 没有提供page参数时自动重定向到第一页
    page = int(request.args.get('page', 1))
    aid = request.args.get('aid', None)

    posts, pagination = sql.get_all_articles(page=page, per_page=10)
    if aid is None:
        return render_template('article.html', article_active=True, posts=posts,
                               pagination=pagination, page=page)
    else:
        # 从posts中找到对应aid的文章赋值给post
        aid = int(aid)
        post = None
        for p in posts:
            if p.id == aid:
                post = p
        if post:
            username = sql.get_username_by_id()  # 一个用户名字典{用户id:用户名}
            all_comment = sql.get_all_comment(aid)  # 文章所有评论
            comment_form = CommentForm(request.form)  # 评论表单
            sql.add_view(aid)  # 增加一次访问量
            return render_template('article-detail.html', article_active=True, page=page,
                                   post=post, username=username, all_comment=all_comment,
                                   comment_form=comment_form, reversed=reversed,
                                   admin_uid=app.config['ADMIN_UID'])
        return redirect(url_for('article', page=page))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username, password = request.form['username'], request.form['password']
        result, message = sql.check_user_password(username, password)
        if result:
            session['logged_in'] = True
            session['uid'] = sql.is_existing_user(username).id
            session['username'] = username
            flash(category="success", message=message)
            return redirect(url_for('article'))
        flash(category="error", message=message)
    else:
        for error in form.errors.values():
            flash(category="error", message=error[0])
    return render_template('login.html', register_login_active=True, form=form)


@app.route('/logout')
def logout():
    if session.pop('logged_in', None):
        session.pop('uid', None)
        username = session.pop('username', None)
        flash(category="success", message="用户 {} 登出成功".format(username))
    else:
        flash(category="warning", message="用户未登录")
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        result, message = sql.add_user(request.form['username'],
                                       request.form['password'],
                                       request.form['email'])
        flash(category="success" if result else "error", message=message)
        return redirect(url_for('login'))
    else:
        for error in form.errors.values():
            flash(category="error", message=error[0])
    return render_template('register.html', register_login_active=True, form=form)


@app.route('/article/add', methods=['POST'])
@check_login
def add():
    aid = request.args.get('aid', None)
    page = request.args.get('page', 1)
    form = CommentForm(request.form)
    if aid and form.validate_on_submit():
        sql.add_comment(aid=aid, content=request.form['content'],
                        uid=session['uid'], cid=request.form['reply'])
        flash(category="success", message="评论成功")
    else:
        for error in form.errors.values():
            flash(category="error", message=error[0])
    return redirect(url_for('article', page=page, aid=aid))


@app.route('/article/del')
@check_login
def del_comment():
    aid = request.args.get('aid', None)
    cid = request.args.get('cid', None)
    page = request.args.get('page', 1)
    print(aid, cid, page)
    if aid and cid and sql.del_comment(aid, session['uid'], cid):
        flash(category="success", message="删除成功")
        return "OK"
    else:
        flash(category="error", message="删除失败")
        return "ERROR"


@app.route('/user_setting', methods=['GET', 'POST'])
@check_login
def user_setting():
    form = UserSettingForm(request.form)
    if request.method == 'GET':
        user = sql.is_existing_user(uid=session['uid'])
        return render_template('user-setting.html', form=form, user=user)
    else:
        if form.validate_on_submit():
            result, message = sql.set_user(uid=session['uid'],
                                           origin_password=request.form.get('origin_password', None),
                                           username=request.form.get('username', None),
                                           new_password=request.form.get('new_password', None),
                                           email=request.form.get('email', None))
            session['username'] = sql.is_existing_user(uid=session['uid']).username
            flash(category="success" if result else "error", message=message)
        else:
            for error in form.errors.values():
                flash(category="error", message=error[0])
    return redirect(url_for('user_setting'))


# 管理员界面
@app.route('/admin')
@check_admin
def admin():
    return redirect(url_for('admin_article', page=1))


@app.route('/admin/article', methods=['GET', 'POST'])
@check_admin
def admin_article():
    page = int(request.args.get('page', 1))
    aid = request.args.get('aid', None)
    posts, pagination = sql.get_all_articles(page=page, per_page=10)
    # 判断是访问的具体文章还是文章列表
    if aid:
        aid = int(aid)
        if request.method == 'GET':
            for p in posts:
                if p.id == aid:
                    return json.dumps({'title': p.title,
                                       'content': p.body})
            return None
        if request.method == 'POST':
            if sql.modify_article(aid=aid,
                                  title=request.form.get('title', None),
                                  body=request.form.get('content', None)):
                flash(category="success", message="修改文章成功")
            else:
                flash(category="error", message="修改文章失败")
            return redirect(url_for('admin_article', page=page))

    return render_template('admin/article.html', article_active=True, posts=posts,
                           pagination=pagination, page=page)


@app.route('/admin/article/add', methods=['POST'])
@check_admin
def admin_add_article():
    page = int(request.args.get('page', 1))
    if sql.add_article(title=request.form['title'],
                       body=request.form['content'],
                       author=app.config['ADMIN_UID']):
        flash(category="success", message="添加文章成功")
    else:
        flash(category="error", message="添加文章失败")
    return redirect(url_for('admin_article', page=page))


@app.route('/admin/article/del')
@check_admin
def admin_del_article():
    aid = request.args.get('aid', None)
    if aid and sql.del_article(aid):
        flash(category="success", message="删除成功")
        return "OK"
    else:
        flash(category="error", message="删除失败")
        return "ERROR"


@app.route('/admin/users')
@check_admin
def admin_users():
    return render_template('admin/users.html', users_active=True,
                           users=sql.get_all_user())


@app.route('/admin/users/del')
@check_admin
def del_admin_user():
    uid = request.args.get('uid', None)
    if uid and sql.del_user(uid):
        flash(category='success', message='删除成功')
        return "OK"
    else:
        flash(category='error', message='删除失败')
        return "ERROR"
