def underline_to_camel(name):
    """
    下划线转驼峰
    :param name:
    :return:
    """
    parts = name.split('_')
    camel_name = ''.join(word.title() for word in parts)
    return camel_name


def transform_enum_string(s):
    """
    解析enum类型
    将字符串enum('N','Y') 转换为 ['N','Y']
    :param s:
    :return:
    """
    s = s.strip("enum()")
    s = s.split(',')
    s = [item.strip("'") for item in s]
    return s


def parse_field_type(column_type: str):
    """
    解析数据类型
    输入：bigint，输出：（'bigint', None）
    输入：bigint(20) unsigned，输出：('bigint unsigned', 20)
    输入：varchar(65535)，输出：('varchar', 65535)
    :param column_type:
    :return:
    """
    import re
    match = re.match(r'^(\w+)(?:\((\d+)\))?\s*(\w+)?$', column_type)
    if match:
        if match.group(3):
            field_type = match.group(1) + " " + match.group(3)
        else:
            field_type = match.group(1)
        if match.group(2):
            length = int(match.group(2))
        else:
            length = None
        result = {
            "field_type": field_type,
            "length": length
        }
        return result
    elif 'enum' in column_type:
        enum_values = transform_enum_string(column_type)
        result = {
            "field_type": 'enum',
            "enum_vale": enum_values
        }
        return result
    else:
        return {}
