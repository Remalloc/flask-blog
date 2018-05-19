# Flask Blog
用Flask框架搭建的一个博客，已部署在阿里云 [Remalloc的博客](http://www.remalloc.top)
## 1.结构设计
采用MVP模式设计博客，模型层使用SQLAlchemy做为ORM，视图层使用Jinja2作为模板语言在服务端渲染，控制层负责模型层与视图层交互
