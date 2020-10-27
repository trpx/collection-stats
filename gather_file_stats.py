import sys
import itertools
from pathlib import Path
import click

if __name__ != '__main__':
    raise NotImplementedError()
sys.path.append(Path(__file__).parent)

from collection_stats_collector import CollectionStatsCollector, utils


@click.command()
@click.argument('src_file', type=click.Path(exists=True))
@click.argument('report_file')
@click.option('--plunk', is_flag=True,
              help='don\'t count empty values (null, 0, empty string etc)')
@click.option('--encoding', type=str, default='utf8', help='[utf8|...]')
@click.option('--json_encoding', type=str, default='utf8', help='[utf8|...]')
@click.option('--format', default='json',
              type=click.Choice(['json', 'xml'], case_sensitive=False))
def main(src_file, report_file, plunk, encoding, json_encoding, format):
    src_file = Path(src_file)

    dct = _read_as_dict(src_file, encoding, json_encoding, format)

    if plunk:
        utils.plunk(dct)

    collector = CollectionStatsCollector()

    collector.add(dct)

    report = str(collector)

    for token, replacement in [
        ['OrderedDict', 'assoc_array'],
        ['OrderedDict', 'assoc_array'],
        [' NoneType', ' null'],
        [' str ', ' string ']
    ]:
        report = report.replace(token, replacement)

    with open(report_file, mode='w', encoding='utf8') as f:
        f.write(report)


def _read_as_dict(file, encoding, json_encoding, format):
    readers = {
        'json': utils.read_json,
        'xml': utils.read_xml,
    }
    format = format or 'json'
    main_reader = readers.pop(format)
    errors = []
    for reader_func in itertools.chain([main_reader], readers.values()):
        try:
            return reader_func(file)
        except Exception as exc:
            errors.append(str(exc))
            continue
    error_msg = '\n'.join(errors)
    print(f"Couldn't parse file '{file}'"
          f"\nthe following errors has occurred:"
          f"\n{error_msg}", file=sys.stderr)
    sys.exit(1)


main()
