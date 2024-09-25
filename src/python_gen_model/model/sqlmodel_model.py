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
import decimal
from datetime import datetime

from .abstract_model import AbstractPrintModel
from .model_utils import underline_to_camel, parse_field_type
from ..enum.enum import ModelType

HEADER = """
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


class SqlmodelPrintModel(AbstractPrintModel):

    def model_type(self):
        return ModelType.SQLMODEL.value

    def print_header(self, **kwargs):
        print(HEADER)

    def print_model(self, table, rows):
        if not rows:
            return
        print()
        print('class %s(SQLModel, table=True):' % underline_to_camel(table))
        # 输出注释
        print(f'    """ {rows[0]["table_comment"]} """')
        print('    __tablename__ = "%s"' % table)

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
                    if primary_key == column_name:
                        print('    # 主键自增，python代码中可以不指定该值')
                        print(
                            f"    {column_name}: Optional[{field.__name__}] = Field(default=None, primary_key=True, description='{column_comment}')")
                    elif "gmt_create" == column_name:
                        print(
                            f"    {column_name}: {filed_type_str} = Field(nullable={is_nullable}, default_factory=datetime.now, description='{column_comment}')")
                    elif "gmt_modified" == column_name:
                        print(
                            f"    {column_name}: {filed_type_str} = Field(nullable={is_nullable}, default_factory=datetime.now, description='{column_comment}')")
                    elif 'varchar' in field_type:
                        length = column_type['length']
                        print(
                            f"    {column_name}: {filed_type_str} = Field(nullable={is_nullable}, max_length={length}, default={column_default}, description='{column_comment}')")
                    else:
                        print(
                            f"    {column_name}: {filed_type_str} = Field(nullable={is_nullable}, default={column_default}, description='{column_comment}')")
