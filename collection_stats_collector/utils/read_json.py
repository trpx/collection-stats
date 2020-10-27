import json


def read_json(file, encoding='utf8', json_encoding='utf8'):
    """
    :param file:
    :param encoding:
    :param json_encoding
    :return:
    """
    with open(file, mode='r', encoding=encoding) as fh:
        return json.loads(fh.read(), encoding=json_encoding)
