import os
import sys
import xmltodict
import xmlschema


def read_xml(
        file,
        encoding='utf8',
        process_namespaces=False,
        xml_namespaces=None,
        xml_schema_file=None,
        no_validate_schema=False,
        **kwargs):
    """
    :param file:
    :param encoding:
    :param process_namespaces:  see https://github.com/martinblech/xmltodict
    :param xml_namespaces:  see https://github.com/martinblech/xmltodict
    :param xml_schema_file:  xsd file, if provided, the xml file is validated against the schema,
                        and this (better) parser is used https://pypi.org/project/xmlschema/
    :param no_validate_schema:  do not validate file against xml schema file
                                (malformed xml file can still cause exceptions etc)
    :param kwargs:  ignored
    :return:
    """
    xml_schema = None
    if xml_schema_file:
        xml_schema = xmlschema.XMLSchema(xml_schema_file)
    kwargs = dict(process_namespaces=process_namespaces)
    if xml_namespaces:
        kwargs.update(process_namespaces=True, namespaces=xml_namespaces)
    with open(file, mode='r', encoding=encoding) as fh:
        if xml_schema is not None:
            if not no_validate_schema:
                validation_msg = f"Validation of xsd on target xml"
                if not xml_schema.is_valid(fh):
                    print(validation_msg+" FAILED!", file=sys.stderr)
                    sys.exit(1)
                else:
                    print(validation_msg+" PASSED.", file=sys.stderr)
            fh.seek(os.SEEK_SET)
            return xml_schema.to_dict(fh)
        return xmltodict.parse(fh.read(), namespaces=xml_namespaces)

