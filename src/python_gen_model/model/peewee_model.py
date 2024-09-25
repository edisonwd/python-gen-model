"""
Field types table参考文档: https://peewee.readthedocs.io/en/latest/peewee/models.html
"""

from peewee import *

from .abstract_model import AbstractPrintModel
from .model_utils import underline_to_camel, parse_field_type
from ..enum.enum import ModelType

HEADER = """
from peewee import *
from datetime import datetime

database = MySQLDatabase('{database}', **{{'host': '{host}', 'port': {port}, 'user': '{user}', 'password': '{password}'}})

"""

BASE_MODEL = """\
class BaseModel(Model):
    class Meta:
        database = database
"""

UNKNOWN_FIELD = """\
class UnknownField(object):
    def __init__(self, *_, **__): pass
"""

FILED_MAPPING = {
    'bigint': BigIntegerField,
    'varchar': CharField,
    'enum': CharField,
    'text': TextField,
    'datetime': DateTimeField,
    'timestamp': DateTimeField,
    'date': DateField,
    'time': TimeField,
    'float': FloatField,
    'double': DoubleField,
    'decimal': DecimalField,
    'tinyint': BooleanField,
    'mediumint': IntegerField,
    'smallint': IntegerField,
    'bigint unsigned': BigIntegerField,
    'int unsigned': IntegerField,
    'mediumint unsigned': IntegerField,
    'smallint unsigned': IntegerField,
    'tinyint unsigned': IntegerField,
    'bit': BitField,
    'blob': BlobField,
    'tinyblob': BlobField,
    'mediumblob': BlobField,
}


class PeeweePrintModel(AbstractPrintModel):

    def model_type(self):
        return ModelType.PEEWEE.value

    def print_header(self, **kwargs):
        header = HEADER.format(**kwargs)
        print(header)

        print(BASE_MODEL)

        print(UNKNOWN_FIELD)

    def print_model(self, table, rows):
        if not rows:
            return
        print('class %s(BaseModel):' % underline_to_camel(table))
        # 输出注释
        print(f'    """ {rows[0]["table_comment"]} """')
        for row in rows:
            column_name = row.get('column_name')
            column_type = row.get('column_type')
            column_comment = row.get('column_comment')
            column_default = row.get('column_default')
            primary_key = row.get('primary_key')
            is_nullable = True if row['is_nullable'] == 'YES' else False

            if 'timestamp' in column_type and column_default == 'CURRENT_TIMESTAMP':
                column_default = 'None'
            elif column_default and type(column_default) == str:
                column_default = f"'{column_default}'"

            column_type = parse_field_type(column_type)

            if column_type:
                field_type = column_type['field_type']
                field = FILED_MAPPING.get(field_type)
                if field:
                    if 'varchar' in field_type:
                        length = column_type['length']
                        print(
                            f"    {column_name} = {field.__name__}(null={is_nullable}, column_name='{column_name}', max_length={length}, default={column_default}, help_text='{column_comment}')")
                    elif 'enum' in field_type:
                        enum_values = column_type['enum_vale']
                        print(
                            f"    {column_name} = {field.__name__}(null={is_nullable}, column_name='{column_name}', choices={enum_values}, default={column_default}, help_text='{column_comment}')")
                    else:
                        print(
                            f"    {column_name} = {field.__name__}(null={is_nullable}, column_name='{column_name}', default={column_default}, help_text='{column_comment}')")
        print('')
        print('    class Meta:')
        print('        table_name = \'%s\'' % table)
        print('')
