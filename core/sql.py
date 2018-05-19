from core import db, bcrypt
from .modle import User, Article, Comments, app


def is_existing_user(username: str = None, uid=None):
    # 检查用户是否存在,存在返回User对象,否则返回None
    if uid:
        return User.query.filter_by(id=uid).first()
    elif username:
        return User.query.filter_by(username=username).first()


def is_existing_email(email: str):
    # 检查邮箱是否存在,存在返回User对象,否则返回None
    return User.query.filter_by(email=email).first()


def is_existing_article(aid: int):
    # 检查文章是否存在,存在返回Article对象,否则返回None
    aid = int(aid)
    return Article.query.filter_by(id=aid).first()


def add_user(username: str, password: str, email: str):
    # 添加用户,返回一个元组 (插入结果(Bool),提示信息)
    # 检测用户是否存在
    if is_existing_user(username):
        return False, "用户已存在"

    # 检测邮箱是否被注册
    if is_existing_email(email):
        return False, "邮箱已注册"

    # 插入用户信息
    pw_hash = bcrypt.generate_password_hash(password)  # hash加密用户密码
    user = User(username=username, password=pw_hash, email=email)
    db.session.add(user)
    db.session.commit()
    return True, "注册成功"


def set_user(uid, origin_password, username=None, new_password=None, email=None):
    user = is_existing_user(uid=uid)
    if user and bcrypt.check_password_hash(user.password, origin_password):
        if username:
            if is_existing_user(username):
                return False, "用户已存在"
            user.username = username
        if new_password:
            user.password = bcrypt.generate_password_hash(new_password)
        if email:
            if is_existing_email(email):
                return False, "邮箱已注册"
            user.email = email
        db.session.commit()
        return True, "更新用户信息成功"
    else:
        return False, "用户不存在或密码错误"


def del_user(uid):
    user = is_existing_user(uid=uid)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    else:
        return False


def get_all_user():
    return User.query.order_by(User.register_date.desc()).all()


def check_user_password(username: str, password: str):
    # 检查用户密码,返回一个元组 (检查结果(Bool),提示信息)
    user = is_existing_user(username)

    if user and bcrypt.check_password_hash(user.password, password):
        return True, "登陆成功"
    else:
        return False, "用户不存在或密码错误"


def get_all_articles(page=None, per_page=None):
    pagination = Article.query.order_by(Article.pub_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    return posts, pagination


def add_article(title: str, body: str, author: int):
    user = is_existing_user(uid=author)
    if user:
        article = Article(title=title, body=body, author=author)
        db.session.add(article)
        db.session.commit()
        return True
    else:
        return False


def modify_article(aid: int, title=None, body=None, author=None):
    article = is_existing_article(aid)
    if article:
        if title:
            article.title = title
        if body:
            article.body = body
        if author:
            article.author = author
        db.session.commit()
        return True
    else:
        return False


def del_article(aid: int):
    article = is_existing_article(aid)
    if article:
        db.session.delete(article)
        db.session.commit()
        return True
    else:
        return False


def add_comment(aid: int, uid: int, content: str, cid=None):
    comments = Comments(aid)
    if comments:
        if not cid:
            comments.add(str(content), int(uid))
        else:
            comments.add(str(content), int(uid), cid)
        return True
    else:
        return False


def del_comment(aid: int, uid: int, cid):
    comments = Comments(aid)
    if comments:
        comment = comments.get_comment(cid)
        # 验证评论用户是否与删除人相同,管理员除外
        if comment and (comment['uid'] == uid or uid == app.config['ADMIN_UID']):
            if comments.del_comment(cid):
                return True
    return False


def get_all_comment(aid: int):
    return Comments(aid).all_comment


def add_view(aid: int):
    article = is_existing_article(aid)
    if article:
        article.views += 1
        db.session.commit()


def get_username_by_id():
    return {user.id: user.username for user in User.query.all()}


def get_email(uid):
    user = is_existing_user(uid=uid)
    if user:
        return user.email
