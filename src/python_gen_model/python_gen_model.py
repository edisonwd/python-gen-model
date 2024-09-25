import pymysql
import sys
from urllib.parse import quote_plus
from .model.abstract_model import AbstractPrintModel

# ob数据库连接配置
config = {
    # python操作ob参考文档：https://yuque.antfin.com/middleware/zdal/python-quick-start
    'user': f'{quote_plus("xx:amlregservermodel:xx")}',  # 用户名
    # Mesh 模式用 xx:{appName}:xx
    # 集群  模式用 xx:{appName}:{身份}
    'password': '',  # 主站为空
    'host': '127.0.0.1',  # 访问地址
    # Mesh 模式用 127.0.0.1
    # 集群  模式用 zdas-pool.{domainname}
    'port': 11306,  # ZDAS 服务器端口号
    'database': 'amlregservermodel_single_dbmesh',
}


def err(msg):
    sys.stderr.write('\033[91m%s\033[0m\n' % msg)
    sys.stderr.flush()


def get_value(column_list: list, key: str):
    """
    获取列值
    :param column_list:
    :param key:
    :return:
    """
    try:
        index = column_list.index(key)
        column_value = column_list[index + 1]
        column_value = column_value.strip("'")
    except ValueError as e:
        column_value = None
    return column_value


def get_rows(create_table_str: str):
    """
    将 mysql 建表语句转换为字典

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

    :param create_table_str:
    :return:
    """
    rows = []
    import re
    if not create_table_str:
        return rows

    result = re.search(r"COMMENT\s?=\s?'(.+?)'", create_table_str)
    if result:
        table_comment = result.group(1)
    else:
        table_comment = ''
    # 将 mysql 建表语句转换为字典
    create_table_str = create_table_str.replace('`', '')
    fields = create_table_str.split('\n')
    search_string = "PRIMARY KEY"
    indices = [i for i, x in enumerate(fields) if search_string in x]
    # 没有主键，返回None
    if len(indices) == 0:
        return rows
    primary_key_index = indices[0]
    primary_key = fields[primary_key_index].strip().strip(",").split(' ')[-1].strip("(").strip(")")
    fields = fields[1:primary_key_index]
    for field in fields:
        column_list = field.strip().strip(",").split(' ')
        column_name = column_list[0]
        column_type = column_list[1]
        column_comment = get_value(column_list, 'COMMENT')
        column_default = get_value(column_list, 'DEFAULT')
        if column_default == 'NULL':
            column_default = None
        if 'NOT NULL' not in field and 'NULL' in field:
            is_nullable = 'YES'
        elif 'NOT NULL' in field:
            is_nullable = 'NO'
        else:
            is_nullable = 'YES'
        row = {
            'column_name': column_name,
            'column_type': column_type,
            'column_comment': column_comment,
            'column_default': column_default,
            'is_nullable': is_nullable,
            'table_comment': table_comment,
            'primary_key': primary_key,
        }
        rows.append(row)

    return rows


# 执行查询的函数
def print_models(tables, connect, orm: str = None):
    connection = pymysql.connect(**connect)
    try:
        # 使用 cursor() 方法创建一个游标对象 cursor
        with connection.cursor() as cursor:
            sub_dict = AbstractPrintModel.get_all_print_models()
            print_model: AbstractPrintModel = sub_dict.get(orm)
            if not print_model:
                raise Exception(f"{orm}模型不存在, 允许传入的 orm: {sub_dict.keys()}")

            # 打印表头
            print_model.print_header(**config)

            for table in tables:
                # 执行查询语句以获取表结构信息
                # 使用预定义语句和参数
                # 替换为你的表名
                sql = f"show create table {table}"
                cursor.execute(sql)
                # 获取所有记录列表
                results = cursor.fetchall()
                for row in results:
                    table_name = row[0]
                    table_create_str = row[1]
                    results = get_rows(table_create_str)
                    # 打印表结构信息
                    print_model.print_model(table=table_name, rows=results)

    except pymysql.MySQLError as e:
        err(f"Error: {e}")
    finally:
        # 关闭数据库连接
        connection.close()
