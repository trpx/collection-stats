import xmltodict


def read_xml(file, encoding='utf8', process_namespaces=False, xml_namespaces=None):
    """
    :param file:
    :param encoding:
    :param process_namespaces:  see https://github.com/martinblech/xmltodict
    :param xml_namespaces:  see https://github.com/martinblech/xmltodict
    :return:
    """
    kwargs = dict(process_namespaces=process_namespaces)
    if xml_namespaces:
        kwargs.update(process_namespaces=True, namespaces=xml_namespaces)
    with open(file, mode='r', encoding=encoding) as fh:
        return xmltodict.parse(fh.read(), namespaces=xml_namespaces)
