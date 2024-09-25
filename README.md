
## python-gen-model
### 项目背景
在使用python操作mysql数据库时，需要生成数据库表对应的Model类（在Java中叫实体类），
本项目用来根据表结构自动生成python的ORM库对应的Model类。

实现原理：**根据数据库创建表的语句自动生成数据表对应的Model类**

支持如下框架：
- Peewee
    - Peewee是一个小型、灵活且易于使用的Python ORM框架，用于与SQL数据库进行交互。它提供了简单、清晰的API，使得在Python中进行数据库操作更加方便。

- SQLModel
    - SQLModel是一个用于SQLAlchemy的Python库，它提供了一种定义数据模型的简单方式，并根据这些定义生成数据库模式和操作数据的方法。

- Tortoise
    - Tortoise是一个异步ORM（对象关系映射）框架，用于在Python中进行数据库操作。它支持异步操作和异步IO，能够轻松地与异步Web框架（如FastAPI）集成。

- Pydantic
    - Pydantic是一个用于数据验证和序列化的Python库，它能够根据给定的数据模型定义自动生成验证器和序列化器，并且具有良好的性能和易用的API。它通常与其他框架（如FastAPI）一起使用，用于验证请求数据和序列化响应数据。

### 安装方法

#### 源码安装
```shell
git clone https://github.com/edisonwd/python-gen-model.git

cd python-gen-model

pip install -e .
```

### 使用方法
```shell
 % python-gen-model -h
Usage: python-gen-model [options] database_name

Options:
  -h, --help            show this help message and exit
  -H HOST, --host=HOST  
  -p PORT, --port=PORT  
  -u USER, --user=USER  
  -P, --password        
  -o ORM, --orm=ORM     Choose an ORM to generate code , support: ['peewee',
                        'sqlmodel', 'tortoise', 'pydantic']. default: sqlmodel
  -t TABLES, --tables=TABLES
                        Only generate the specified tables. Multiple table
                        names should be separated by commas.

```
### 使用示例

使用docker 创建一个mysql数据库，并创建一张表：
```shell
docker run -d --name mysql_test -p 11306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql

docker exec -it mysql_test bash

mysql -uroot -p123456

create database my_database;

use my_database;
```

```sql
CREATE TABLE `kb_document` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `gmt_create` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `gmt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `doc_id` varchar(64) NOT NULL COMMENT '文档ID',
  `doc_name` varchar(128) NOT NULL COMMENT '文档名称',
  `location` varchar(512) DEFAULT NULL COMMENT '文档位置',
  `kb_id` varchar(64) NOT NULL COMMENT '知识库ID',
  `doc_type` varchar(64) NOT NULL COMMENT '文档类型',
  `doc_status` varchar(64) NOT NULL COMMENT '文档状态',
  `doc_content` longtext DEFAULT NULL COMMENT '文档内容',
  `doc_version` int(11) NOT NULL COMMENT '文档版本',
  `doc_parent` varchar(64) DEFAULT NULL COMMENT '文档父节点',
  `doc_path` varchar(512) DEFAULT NULL COMMENT '文档路径',
  `doc_creator` varchar(64) NOT NULL COMMENT '文档创建者',
  `doc_modifier` varchar(64) NOT NULL COMMENT '文档修改者',
  `doc_ext` varchar(512) DEFAULT NULL COMMENT '文档扩展信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_doc_id` (`doc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='文档表';

CREATE TABLE `kb_tag` (
  `id` bigint( 20 ) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `gmt_create` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `gmt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `tag_id` varchar(64) NOT NULL COMMENT '标签ID',
  `tag_name` varchar(128) NOT NULL COMMENT '标签名称',
  `tag_type` varchar(64) NOT NULL COMMENT '标签类型',
  `tag_status` varchar(64) NOT NULL COMMENT '标签状态',
  `tag_creator` varchar(64) NOT NULL COMMENT '标签创建者',
  `tag_modifier` varchar(64) NOT NULL COMMENT '标签修改者',
  `tag_ext` varchar(512) DEFAULT NULL COMMENT '标签扩展信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tag_id` (`tag_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='标签表';
  
```

#### 生成sqlmodel的Model类
直接生成OB表对应sqlmodel的Model类：
```shell
python-gen-model -H 127.0.0.1 -p 11306 -u root -P  -o sqlmodel -t kb_document,kb_tag my_database 
```
输出内容如下：
```python
from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Optional
from api.config import settings
from datetime import datetime

engine = create_engine(settings.DATABASE_URI, echo=True)


def create_db_and_tables():
  SQLModel.metadata.create_all(engine)


def get_session():
  with Session(engine) as session:
    yield session


class KbDocument(SQLModel, table=True):
  """ 文档表 """
  __tablename__ = "kb_document"
  # 主键自增，python代码中可以不指定该值
  id: Optional[int] = Field(default=None, primary_key=True, description='主键')
  gmt_create: datetime = Field(nullable=False, default_factory=datetime.now, description='创建时间')
  gmt_modified: datetime = Field(nullable=False, default_factory=datetime.now, description='修改时间')
  doc_id: str = Field(nullable=False, max_length=64, default=None, description='文档ID')
  doc_name: str = Field(nullable=False, max_length=128, default=None, description='文档名称')
  location: Optional[str] = Field(nullable=True, max_length=512, default=None, description='文档位置')
  kb_id: str = Field(nullable=False, max_length=64, default=None, description='知识库ID')
  doc_type: str = Field(nullable=False, max_length=64, default=None, description='文档类型')
  doc_status: str = Field(nullable=False, max_length=64, default=None, description='文档状态')
  doc_content: Optional[str] = Field(nullable=True, default=None, description='文档内容')
  doc_version: int = Field(nullable=False, default=None, description='文档版本')
  doc_parent: Optional[str] = Field(nullable=True, max_length=64, default=None, description='文档父节点')
  doc_path: Optional[str] = Field(nullable=True, max_length=512, default=None, description='文档路径')
  doc_creator: str = Field(nullable=False, max_length=64, default=None, description='文档创建者')
  doc_modifier: str = Field(nullable=False, max_length=64, default=None, description='文档修改者')
  doc_ext: Optional[str] = Field(nullable=True, max_length=512, default=None, description='文档扩展信息')

class KbTag(SQLModel, table=True):
  """ 标签表 """
  __tablename__ = "kb_tag"
  # 主键自增，python代码中可以不指定该值
  id: Optional[int] = Field(default=None, primary_key=True, description='主键')
  gmt_create: datetime = Field(nullable=False, default_factory=datetime.now, description='创建时间')
  gmt_modified: datetime = Field(nullable=False, default_factory=datetime.now, description='修改时间')
  tag_id: str = Field(nullable=False, max_length=64, default=None, description='标签ID')
  tag_name: str = Field(nullable=False, max_length=128, default=None, description='标签名称')
  tag_type: str = Field(nullable=False, max_length=64, default=None, description='标签类型')
  tag_status: str = Field(nullable=False, max_length=64, default=None, description='标签状态')
  tag_creator: str = Field(nullable=False, max_length=64, default=None, description='标签创建者')
  tag_modifier: str = Field(nullable=False, max_length=64, default=None, description='标签修改者')
  tag_ext: Optional[str] = Field(nullable=True, max_length=512, default=None, description='标签扩展信息')


```

#### 生成peewee的Model类
```shell
python-gen-model -H 127.0.0.1 -p 11306 -u root -P  -o peewee -t kb_document,kb_tag my_database 
```
输出内容如下：
```python
from peewee import *
from datetime import datetime

database = MySQLDatabase('my_database', **{'host': '127.0.0.1', 'port': 11306, 'user': 'root', 'password': '123456'})


class BaseModel(Model):
    class Meta:
        database = database

class UnknownField(object):
    def __init__(self, *_, **__): pass

class KbDocument(BaseModel):
    """ 文档表 """
    id = BigIntegerField(null=False, column_name='id', default=None, help_text='主键')
    gmt_create = DateTimeField(null=False, column_name='gmt_create', default=None, help_text='创建时间')
    gmt_modified = DateTimeField(null=False, column_name='gmt_modified', default=None, help_text='修改时间')
    doc_id = CharField(null=False, column_name='doc_id', max_length=64, default=None, help_text='文档ID')
    doc_name = CharField(null=False, column_name='doc_name', max_length=128, default=None, help_text='文档名称')
    location = CharField(null=True, column_name='location', max_length=512, default=None, help_text='文档位置')
    kb_id = CharField(null=False, column_name='kb_id', max_length=64, default=None, help_text='知识库ID')
    doc_type = CharField(null=False, column_name='doc_type', max_length=64, default=None, help_text='文档类型')
    doc_status = CharField(null=False, column_name='doc_status', max_length=64, default=None, help_text='文档状态')
    doc_parent = CharField(null=True, column_name='doc_parent', max_length=64, default=None, help_text='文档父节点')
    doc_path = CharField(null=True, column_name='doc_path', max_length=512, default=None, help_text='文档路径')
    doc_creator = CharField(null=False, column_name='doc_creator', max_length=64, default=None, help_text='文档创建者')
    doc_modifier = CharField(null=False, column_name='doc_modifier', max_length=64, default=None, help_text='文档修改者')
    doc_ext = CharField(null=True, column_name='doc_ext', max_length=512, default=None, help_text='文档扩展信息')

    class Meta:
        table_name = 'kb_document'

class KbTag(BaseModel):
    """ 标签表 """
    id = BigIntegerField(null=False, column_name='id', default=None, help_text='主键')
    gmt_create = DateTimeField(null=False, column_name='gmt_create', default=None, help_text='创建时间')
    gmt_modified = DateTimeField(null=False, column_name='gmt_modified', default=None, help_text='修改时间')
    tag_id = CharField(null=False, column_name='tag_id', max_length=64, default=None, help_text='标签ID')
    tag_name = CharField(null=False, column_name='tag_name', max_length=128, default=None, help_text='标签名称')
    tag_type = CharField(null=False, column_name='tag_type', max_length=64, default=None, help_text='标签类型')
    tag_status = CharField(null=False, column_name='tag_status', max_length=64, default=None, help_text='标签状态')
    tag_creator = CharField(null=False, column_name='tag_creator', max_length=64, default=None, help_text='标签创建者')
    tag_modifier = CharField(null=False, column_name='tag_modifier', max_length=64, default=None, help_text='标签修改者')
    tag_ext = CharField(null=True, column_name='tag_ext', max_length=512, default=None, help_text='标签扩展信息')

    class Meta:
        table_name = 'kb_tag'

```


#### 生成tortoise的Model类
```shell
python-gen-model -H 127.0.0.1 -p 11306 -u root -P  -o tortoise -t kb_document,kb_tag my_database 
```
输出内容如下：
```python
from tortoise.fields import *
from tortoise.models import Model
from datetime import datetime


class KbDocument(Model):
  """ 文档表 """
  id = IntField(null=False, source_field='id', default=None, description='主键')
  gmt_create = DatetimeField(null=False, source_field='gmt_create', default=None, description='创建时间')
  gmt_modified = DatetimeField(null=False, source_field='gmt_modified', default=None, description='修改时间')
  doc_id = CharField(null=False, source_field='doc_id', max_length=64, default=None, description='文档ID')
  doc_name = CharField(null=False, source_field='doc_name', max_length=128, default=None, description='文档名称')
  location = CharField(null=True, source_field='location', max_length=512, default=None, description='文档位置')
  kb_id = CharField(null=False, source_field='kb_id', max_length=64, default=None, description='知识库ID')
  doc_type = CharField(null=False, source_field='doc_type', max_length=64, default=None, description='文档类型')
  doc_status = CharField(null=False, source_field='doc_status', max_length=64, default=None, description='文档状态')
  doc_content = TextField(null=True, source_field='doc_content', default=None, description='文档内容')
  doc_version = IntField(null=False, source_field='doc_version', default=None, description='文档版本')
  doc_parent = CharField(null=True, source_field='doc_parent', max_length=64, default=None, description='文档父节点')
  doc_path = CharField(null=True, source_field='doc_path', max_length=512, default=None, description='文档路径')
  doc_creator = CharField(null=False, source_field='doc_creator', max_length=64, default=None, description='文档创建者')
  doc_modifier = CharField(null=False, source_field='doc_modifier', max_length=64, default=None, description='文档修改者')
  doc_ext = CharField(null=True, source_field='doc_ext', max_length=512, default=None, description='文档扩展信息')

  class Meta:
    table = 'kb_document'

class KbTag(Model):
  """ 标签表 """
  id = IntField(null=False, source_field='id', default=None, description='主键')
  gmt_create = DatetimeField(null=False, source_field='gmt_create', default=None, description='创建时间')
  gmt_modified = DatetimeField(null=False, source_field='gmt_modified', default=None, description='修改时间')
  tag_id = CharField(null=False, source_field='tag_id', max_length=64, default=None, description='标签ID')
  tag_name = CharField(null=False, source_field='tag_name', max_length=128, default=None, description='标签名称')
  tag_type = CharField(null=False, source_field='tag_type', max_length=64, default=None, description='标签类型')
  tag_status = CharField(null=False, source_field='tag_status', max_length=64, default=None, description='标签状态')
  tag_creator = CharField(null=False, source_field='tag_creator', max_length=64, default=None, description='标签创建者')
  tag_modifier = CharField(null=False, source_field='tag_modifier', max_length=64, default=None, description='标签修改者')
  tag_ext = CharField(null=True, source_field='tag_ext', max_length=512, default=None, description='标签扩展信息')

  class Meta:
    table = 'kb_tag'


```


#### 生成pydantic的Model类
```shell
python-gen-model -H 127.0.0.1 -p 11306 -u root -P  -o pydantic -t kb_document,kb_tag my_database 
```
输出内容如下：
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class KbDocument(BaseModel):
    """ 文档表 """
    id: int = Field(default=None, description='主键')
    gmt_create: datetime = Field(default=None, description='创建时间')
    gmt_modified: datetime = Field(default=None, description='修改时间')
    doc_id: str = Field(max_length=64, default=None, description='文档ID')
    doc_name: str = Field(max_length=128, default=None, description='文档名称')
    location: Optional[str] = Field(max_length=512, default=None, description='文档位置')
    kb_id: str = Field(max_length=64, default=None, description='知识库ID')
    doc_type: str = Field(max_length=64, default=None, description='文档类型')
    doc_status: str = Field(max_length=64, default=None, description='文档状态')
    doc_content: Optional[str] = Field(default=None, description='文档内容')
    doc_version: int = Field(default=None, description='文档版本')
    doc_parent: Optional[str] = Field(max_length=64, default=None, description='文档父节点')
    doc_path: Optional[str] = Field(max_length=512, default=None, description='文档路径')
    doc_creator: str = Field(max_length=64, default=None, description='文档创建者')
    doc_modifier: str = Field(max_length=64, default=None, description='文档修改者')
    doc_ext: Optional[str] = Field(max_length=512, default=None, description='文档扩展信息')

    def __repr__(self):
        f"""<KbDocument(
        id='{self.id}',
        gmt_create='{self.gmt_create}',
        gmt_modified='{self.gmt_modified}',
        doc_id='{self.doc_id}',
        doc_name='{self.doc_name}',
        location='{self.location}',
        kb_id='{self.kb_id}',
        doc_type='{self.doc_type}',
        doc_status='{self.doc_status}',
        doc_content='{self.doc_content}',
        doc_version='{self.doc_version}',
        doc_parent='{self.doc_parent}',
        doc_path='{self.doc_path}',
        doc_creator='{self.doc_creator}',
        doc_modifier='{self.doc_modifier}',
        doc_ext='{self.doc_ext}',
        )"""
class KbTag(BaseModel):
    """ 标签表 """
    id: int = Field(default=None, description='主键')
    gmt_create: datetime = Field(default=None, description='创建时间')
    gmt_modified: datetime = Field(default=None, description='修改时间')
    tag_id: str = Field(max_length=64, default=None, description='标签ID')
    tag_name: str = Field(max_length=128, default=None, description='标签名称')
    tag_type: str = Field(max_length=64, default=None, description='标签类型')
    tag_status: str = Field(max_length=64, default=None, description='标签状态')
    tag_creator: str = Field(max_length=64, default=None, description='标签创建者')
    tag_modifier: str = Field(max_length=64, default=None, description='标签修改者')
    tag_ext: Optional[str] = Field(max_length=512, default=None, description='标签扩展信息')

    def __repr__(self):
        f"""<KbTag(
        id='{self.id}',
        gmt_create='{self.gmt_create}',
        gmt_modified='{self.gmt_modified}',
        tag_id='{self.tag_id}',
        tag_name='{self.tag_name}',
        tag_type='{self.tag_type}',
        tag_status='{self.tag_status}',
        tag_creator='{self.tag_creator}',
        tag_modifier='{self.tag_modifier}',
        tag_ext='{self.tag_ext}',
        )"""

```


### 参考文档
- [peewee](https://peewee.readthedocs.io/en/latest/peewee/installation.html)
- [tortoise-orm](https://tortoise.github.io/index.html)
- [sqlmodel](https://sqlmodel.tiangolo.com/)
- [pydantic](https://docs.pydantic.dev/latest/)
