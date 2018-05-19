from uuid import uuid1
from datetime import datetime
import json

import pytz

from . import db, app

TIME_ZONE = pytz.timezone(app.config['TIME_ZONE'])


class User(db.Model):
    """
    用户模型
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    register_date = db.Column(db.DateTime, default=datetime.now(tz=TIME_ZONE))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.Column(db.Text, nullable=True)
    views = db.Column(db.Integer, default=0)
    pub_date = db.Column(db.DateTime, default=datetime.now(tz=TIME_ZONE))

    def __repr__(self):
        return '<Article {}>'.format(self.title)


class Comments(object):
    """
    评论模型
    """

    def __new__(cls, aid: int, **kwargs):
        """
        维持一个单例，避免从数据库中反复读取评论
        """
        _comment_instance = '_comment_instance_' + str(aid)
        if not hasattr(Comments, _comment_instance):
            Comments._comment_instance = object.__new__(cls)
        else:
            Comments._comment_instance._comment_instance = aid
        return Comments._comment_instance

    def __init__(self, aid: int):
        self.aid = aid
        # 检查之前是否已经读取过评论
        if not getattr(self, 'all_comment', None):
            # 评论列表:[{cid:ID,content:内容,reply:回复ID,floor:num,pub_date:发布日期}]
            article = Article.query.get(aid)
            if article and article.comments:
                # 读取文章json格式的评论
                self.all_comment = json.loads(article.comments)
            else:
                self.all_comment = []
        if not getattr(self, 'comment_dict', None):
            # 索引字典,用来快速索引到某条评论 {cid:索引}
            self.comment_dict = {}

    def __repr__(self):
        return str(self.all_comment)

    def __getitem__(self, item):
        return self.all_comment[item]

    def __update(self):
        # 更新数据
        article = db.session.query(Article).get(self.aid)
        article.comments = json.dumps(self.all_comment)
        db.session.commit()
        self.all_comment = json.loads(Article.query.get(self.aid).comments)

    def get_comment(self, cid, bulk=False):
        """ 获取与参数cid相等的评论,有返回评论字典,没有返回None """
        for comment in self.all_comment:
            if comment['cid'] == cid:
                return comment
            reply = comment['reply']
            if reply:
                for r in reply:
                    if r['cid'] == cid:
                        if bulk:
                            return comment
                        else:
                            return r

    def __get_floor(self, cid=None):
        """
        :param cid: 评论id号
        :return: 返回最后的楼层+1
        如果cid==None 就是普通楼层,否则为回复楼层,普通楼层与回复楼层分别计算,如:
        #2 我是2楼
         #2 回复2楼,too
         #1 回复2楼
        #1 我是1楼
        """
        if not cid:
            return len(self.all_comment) + 1
        else:
            comment = self.get_comment(cid, bulk=True)
            if comment:
                return len(comment['reply']) + 1

    def add(self, content: str, uid: int, cid=None):
        """
        :param content: 评论内容
        :param uid: 用户id
        :param cid: 评论id,如果提供了表示回复某条评论,没有表示回复文章
        :return: 添加成功会返回评论id,失败返回None
        """

        if cid:
            comment = self.get_comment(cid, bulk=True)
            if comment:
                new_cid = str(uuid1())
                comment['reply'].append({'cid': new_cid, 'content': content, 'reply': None,
                                         'uid': uid, 'floor': self.__get_floor(cid),
                                         'pub_date': str(datetime.now(tz=TIME_ZONE))})
            else:
                return None
        else:
            new_cid = str(uuid1())
            comment = {'cid': new_cid, 'content': content, 'reply': [],
                       'uid': uid, 'floor': self.__get_floor(),
                       'pub_date': str(datetime.now(tz=TIME_ZONE))}
            self.all_comment.append(comment)
        self.__update()
        return new_cid

    def del_comment(self, cid):
        comment = self.get_comment(cid)
        if comment:
            comment['content'] = "[已删除]"
            self.__update()
            return cid
