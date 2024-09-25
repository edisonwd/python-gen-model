import sys
from getpass import getpass
from optparse import OptionParser

import pymysql

from src.python_gen_model.model.abstract_model import AbstractPrintModel

# 数据库连接配置
config = {
    'user': 'root',  # 用户名
    'password': 'infini_rag_flow',  # 密码
    'host': '127.0.0.1',  # 访问地址
    'port': 3306,  # 端口号
    'database': 'rag_flow',  # 数据库名称
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

sql_temp = """
SELECT COLUMN_NAME as column_name, 
        COLUMN_TYPE as column_type, 
        COLUMN_COMMENT as column_comment, 
        COLUMN_DEFAULT as column_default, 
        IS_NULLABLE as is_nullable, 
        EXTRA as extra
FROM information_schema.columns 
WHERE table_name = '%s'
"""


def err(msg):
    sys.stderr.write('\033[91m%s\033[0m\n' % msg)
    sys.stderr.flush()


# 执行查询的函数
def print_models(tables, connect, orm: str = None):
    connection = pymysql.connect(**connect)
    try:
        # 使用 cursor() 方法创建一个游标对象 cursor
        with connection.cursor() as cursor:

            # 执行查询语句以获取所有表的名称
            cursor.execute("SHOW TABLES")
            # 获取结果集
            query_tables = cursor.fetchall()
            all_table_names = [table.get(f'Tables_in_{connect["database"]}') for table in query_tables]
            if tables:
                intersection = list(set(all_table_names) & set(tables))
            else:
                intersection = all_table_names
            if not intersection:
                err(f'指定的表{tables}不存在，可以选择的表如下：{all_table_names}, 不指定默认为所有表')
                sys.exit(1)

            sub_dict = AbstractPrintModel.get_all_print_models()
            print_model: AbstractPrintModel = sub_dict.get(orm)
            if not print_model:
                raise Exception(f"{orm}模型不存在, 允许传入的 orm: {sub_dict.keys()}")

            # 打印表头
            print_model.print_header(**config)

            for table_name in intersection:
                # 执行查询语句以获取表结构信息
                # cursor.execute(sql_temp % table_name)
                sql = f"describe table {table_name}"
                cursor.execute(sql)
                # 获取结果集
                results = cursor.fetchall()
                # 打印表结构信息
                print_model.print_model(table=table_name, rows=results)

    except pymysql.MySQLError as e:
        err(f"Error: {e}")
    finally:
        # 关闭数据库连接
        connection.close()


def get_option_parser():
    parser = OptionParser(usage='usage: %prog [options] database_name')
    ao = parser.add_option
    ao('-H', '--host', dest='host')
    ao('-p', '--port', dest='port', type='int')
    ao('-u', '--user', dest='user')
    ao('-P', '--password', dest='password', action='store_true')
    ao('-o', '--orm', dest='orm', choices=["peewee", "tortoise", "sqlmodel"],
       help='Choose an ORM to generate code for. default: peewee', default='peewee')
    ao('-t', '--tables', dest='tables',
       help=('Only generate the specified tables. Multiple table names should '
             'be separated by commas.'))
    return parser


def main():
    parser = get_option_parser()
    options, args = parser.parse_args()

    if len(args) < 1:
        err('Missing required parameter "database"')
        parser.print_help()
        sys.exit(1)

    database = args[-1]
    config['database'] = database
    if options.host:
        config['host'] = options.host
    if options.port:
        config['port'] = options.port
    if options.user:
        config['user'] = options.user
    if options.password:
        config['password'] = getpass()

    tables = None
    if options.tables:
        tables = [table.strip() for table in options.tables.split(',')
                  if table.strip()]

    print_models(tables, config, options.orm)


if __name__ == '__main__':
    main()
