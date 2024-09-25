"""
在Django中，Tortoise ORM和MySQL表字段的映射对应表可以如下所示：

Tortoise ORM字段	MySQL表字段
CharField	VARCHAR
TextField	TEXT
IntegerField	INT
FloatField	FLOAT
DateTimeField	DATETIME
BooleanField	BOOLEAN
注意：这只是一些常见的字段类型映射，还有其他更多字段类型可以使用，具体取决于您的数据表结构和模型定义。

"""

from .abstract_model import AbstractPrintModel
from .model_utils import underline_to_camel, parse_field_type
from tortoise.fields import *

from ..enum.enum import ModelType

HEADER = """
from tortoise.fields import *
from tortoise.models import Model
from datetime import datetime

"""

FILED_MAPPING = {
    'bigint': IntField,
    'int': IntField,
    'varchar': CharField,
    'enum': CharField,
    'text': TextField,
    'datetime': DatetimeField,
    'timestamp': DatetimeField,
    'decimal': DecimalField,
    'tinyint': BooleanField,
    'date': DateField,
    'time': TimeField,
    'longtext': TextField,
}


class TortoisePrintModel(AbstractPrintModel):

    def model_type(self):
        return ModelType.TORTOISE.value

    def print_header(self, **kwargs):
        print(HEADER)

    def print_model(self, table, rows):
        if not rows:
            return
        print('class %s(Model):' % underline_to_camel(table))
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
                            f"    {column_name} = {field.__name__}(null={is_nullable}, source_field='{column_name}', max_length={length}, default={column_default}, description='{column_comment}')")
                    else:
                        print(
                            f"    {column_name} = {field.__name__}(null={is_nullable}, source_field='{column_name}', default={column_default}, description='{column_comment}')")
        print('')
        print('    class Meta:')
        print('        table = \'%s\'' % table)
        print('')
