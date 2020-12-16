import click
from collection_stats.collection_stats_collector import CollectionStatsCollector, utils
import os
from pathlib import Path
import sys
import traceback
import shutil


@click.command()
@click.argument('src_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('report_file', type=click.Path(file_okay=True, dir_okay=False))
@click.option('--plunk', is_flag=True,
              help='don\'t count empty values (null, 0, "", [], {} etc)'
                   ' and don\'t include them in samples')
@click.option('--encoding', type=str, default='utf8', help='[utf8|...] (of src_file)')
@click.option('--json_encoding', type=str, default='utf8', help='[utf8|...] (of src_file)')
@click.option('--format', default=None,
              type=click.Choice(['csv', 'json', 'xml'], case_sensitive=False))
@click.option('--samples', is_flag=True,
              help="write samples to 'samples' directory alongside the report file")
@click.option('--samples-dir',
              type=click.Path(file_okay=False, dir_okay=True),
              default=None,
              help="write samples to this directory, defaults to report_file/../samples,"
                   " note: will be cleared before the samples are written")
@click.option('--max-samples', type=int, default=100,
              help="max samples to save (used only with --samples flag)")
@click.option(
    '--xsd', default=None,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="xsd file, containing xml schema"
)
@click.option(
    '--no-validate-xsd', is_flag=True,
    help="don't validate xml file against xml schema"
         " (works only if both --xsd option and xml src_file provided)"
)
@click.option('--csv-sep', default=',', type=str, help="col separator, used with csv format only")
@click.option('--debug', is_flag=True, help="prefer more verbose errors (if any)")
def main(
        src_file,
        report_file,
        plunk,
        encoding,
        json_encoding,
        format,
        samples,
        samples_dir,
        max_samples,
        xsd,
        no_validate_xsd,
        csv_sep,
        debug,
):
    """
    Calculate and save a report about the structure of xml/json file, it's fields'
    types and lengths etc. Optionally dump samples and validate xml file against xml schema.
    """
    src_file = Path(src_file)
    report_file = Path(report_file)
    os.makedirs(report_file.parent, exist_ok=True)
    if report_file.is_file():
        report_file.unlink()
    samples = samples or samples_dir
    samples_dir = Path(samples_dir) if samples_dir else report_file.parent.joinpath('samples')
    if samples and samples_dir.is_dir():
        shutil.rmtree(samples_dir)

    format, dct = _read_as_dict(
        src_file,
        encoding=encoding,
        json_encoding=json_encoding,
        format=format,
        xml_schema_file=xsd,
        no_validate_xml_schema=no_validate_xsd,
        csv_sep=csv_sep,
        debug=debug,
    )

    if plunk:
        utils.plunk(dct)

    collector = CollectionStatsCollector()

    collector.add(dct)

    report = str(collector)

    with report_file.open(mode='w', encoding='utf8') as f:
        f.write(report+'\n')
        print(f"written '{report_file}'", file=sys.stderr)

    if not samples:
        return

    samples_writer = utils.SamplesWriter(
        samples_dir,
        max_samples=max_samples,
        is_xml_like=format == 'xml',
    )
    samples_writer.write(dct)


def _read_as_dict(
        file,
        *,
        encoding,
        json_encoding,
        format,
        xml_schema_file,
        no_validate_xml_schema,
        csv_sep,
        debug,
):
    readers = {
        'xml': utils.read_xml,
        'csv': utils.read_csv,
        'json': utils.read_json,
    }
    format = format or (file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else None)
    main_reader = readers.pop(format, None)
    if main_reader is not None:
        readers = {
            format: main_reader,
        }
    formats_errors = {}
    for format, reader_func in readers.items():
        try:
            dct = reader_func(
                file,
                encoding=encoding,
                json_encoding=json_encoding,
                xml_schema_file=xml_schema_file,
                no_validate_schema=no_validate_xml_schema,
                sep=csv_sep,
            )
            return format, dct
        except Exception as exc:
            formats_errors[format] = exc
            continue
    if debug:
        error_msg = ''
        for n, (format, exc) in enumerate(formats_errors.items()):
            error_msg += f'\n\nFormat {repr(format)} error:\n' + _format_exception(exc)
    else:
        error_msg = '\n' + '\n'.join([str(i) for i in formats_errors.values()])
    print(f"Couldn't parse file '{file}'"
          f"\nthe following errors has occurred:"
          f"{error_msg}", file=sys.stderr)

    sys.exit(1)


def _format_exception(e):
    return ''.join(traceback.format_exception(type(e), e, e.__traceback__))
