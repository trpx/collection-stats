

# What is this

Cli util and a module to gather statistics on what is inside an  
xml/json file and generate a handy humanized report.

Also lets to dump fields' samples to a directory structure which  
resembles the analyzed xml/json structure.


# How to install and run

install:  
`pip install git+https://github.com/trpx/collection-stats`

run e.g.:  
`collection-stats data.xml dst_dir/report.txt --samples --xsd structure.xsd.xml`
add `--plunk` flag to ignore empty values

see:  
`collection-stats --help`

```
Usage: collection-stats [OPTIONS] SRC_FILE REPORT_FILE

  Calculate and save a report about the structure of xml/json file, it's
  fields' types and lengths etc. Optionally dump samples and validate xml
  file against xml schema.

Options:
  --plunk                  don't count empty values (null, 0, "", [], {} etc)
                           and don't include them in samples

  --encoding TEXT          [utf8|...] (of src_file)
  --json_encoding TEXT     [utf8|...] (of src_file)
  --format [json|xml]
  --samples                write samples to 'samples' directory alongside the
                           report file

  --samples-dir DIRECTORY  write samples to this directory, defaults to
                           report_file/../samples, note: will be cleared
                           before the samples are written

  --max-samples INTEGER    max samples to save (used only with --samples flag)
  --xsd FILE               xsd file, containing xml schema
  --no-validate-xsd        don't validate xml file against xml schema (works
                           only if both --xsd option and xml src_file
                           provided)

  --debug                  prefer more verbose errors (if any)
  --help                   Show this message and exit.
```

## How to install into venv:

1. create venv (if not exists)  
    `python3 -m venv venv`
  
2. activate venv:  
    Mac / Linux:  
    `source venv/bin/activate`  
    Windows:  
    `venv/Scripts/activate.bat`
  
3. install the package:  
  `pip install git+https://github.com/trpx/collection-stats`  

4. run:  
`collection-stats --help`


## Stand-alone stats collector usage:

    from collection_stats import CollectionStatsCollector

    collector = CollectionStatsCollector()

    for collection in some_collections:
        uid = ...  # optional - see below
        collector.add(collection, uid=uid)  # uid is optional (used for include_samples=True)

    print(collector.count)
    print(collector)
    print(collector.format(include_samples=True))
