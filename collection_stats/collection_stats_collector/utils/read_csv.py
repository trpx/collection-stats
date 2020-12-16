import collections
import csv
from io import StringIO
import os


def read_csv(file, *, encoding='utf8', sep=',', keys=(), **kwargs):
    """
    :param file:
    :param encoding:
    :param sep:
    :param keys:  names of columns, if not provided, values of the first row are used
    :return:
    """
    buffer = StringIO()
    with open(file, mode='r', encoding=encoding) as fh:
        buffer.write(fh.read())
    buffer.seek(os.SEEK_SET)
    reader = csv.reader(buffer, delimiter=sep)
    result = collections.defaultdict(list)
    for n, row in enumerate(reader):
        if n == 0:
            if keys:
                continue
            keys = row
            continue
        for k, v in zip(keys, row):
            result[k].append(v)
    return dict(result)
