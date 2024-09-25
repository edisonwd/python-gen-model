"""
用于打印输出数据表对应的 pydantic 模型
"""
import decimal
from datetime import datetime

from .abstract_model import AbstractPrintModel
from .model_utils import underline_to_camel, parse_field_type
from ..enum.enum import ModelType

HEADER = """
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
"""

FILED_MAPPING = {
    'bigint': int,
    'int': int,
    'varchar': str,
    'enum': str,
    'text': str,
    'datetime': datetime,
    'decimal': decimal,
    'tinyint': int,
    'date': datetime,
    'time': datetime,
    'longtext': str,
    'bigint unsigned': int,
    'int unsigned': int,
    'timestamp': datetime,
}


class PydanticPrintModel(AbstractPrintModel):

    def model_type(self):
        return ModelType.PYDANTIC.value

    def print_header(self, **kwargs):
        print(HEADER)

    def print_model(self, table, rows):
        if not rows:
            return
        class_name = underline_to_camel(table)
        print('class %s(BaseModel):' % class_name)
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
            # print(column_type)
            if column_type:
                field_type = column_type['field_type']
                field = FILED_MAPPING.get(field_type)
                if field:
                    filed_type_str = field.__name__
                    if is_nullable:
                        filed_type_str = f'Optional[{field.__name__}]'

                    if 'varchar' in field_type:
                        length = column_type['length']
                        print(
                            f"    {column_name}: {filed_type_str} = Field(max_length={length}, default={column_default}, description='{column_comment}')")
                    else:
                        print(
                            f"    {column_name}: {filed_type_str} = Field(default={column_default}, description='{column_comment}')")
        print()
        print("    def __repr__(self):")
        print(f'        f"""<{class_name}(')
        for row in rows:
            column_name = row.get('column_name')
            print(f"        {column_name}='{{self.{column_name}}}',")

        print(f'        )"""')
