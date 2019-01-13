# Flask Blog
![progressed](http://progressed.io/bar/91?title=done)
**目前版本Flask-admin插件有XSS漏洞**

用Flask框架搭建的一个博客，已部署在阿里云 [Remalloc的博客](http://www.remalloc.top)
## 1.结构设计
采用MVP模式设计博客，**模型层**使用SQLAlchemy做为ORM，**视图层**使用Jinja2作为模板语言在服务端渲染，**控制层**负责模型层与视图层交互
![MVP](https://github.com/Remalloc/flask-blog/blob/master/img/mvp.png)
## 2.功能设计
* 文章使用Markdown编写
* 可修改已发布的博客
* 可查看已注册用户和删除用户
* 支持用户登录注册
* 支持用户评论
* 支持用户修改信息
* 自动分页
* 移动端友好
## 3.模块设计
| 模块 | 目录 | 功能 |
| -------- | :----: | :----: |
| modle.py     | core/ | 储存用户、文章、评论三个模型 |
| page.py        |   core/   |   给视图提供数据和路由分配  |
| sql.py        |    core/    |  提供各类操作数据库功能  |
| \_\_init\_\_.py   |   core/    |  初始化Flask及各类插件  |
| create_database.py |  bin/  |  创建sqlite数据库  |
| run.py  |  ./  | 运行博客  |
## 4.库依赖
[requirements](https://github.com/Remalloc/flask-blog/blob/master/requirements.txt)
## 5.未来功能
* 图片上传
* 点赞、收藏
* 用户消息提醒、私信
* 后台Markdown编辑器



