`prepare_multiqc.py` take multiqc_data.json, which can be found within multiqc_data path after a multiqc run as input.
And either dumps raw data using `--no-decompose` option or decomposes the output into each sample provided in the CLI
using `--decompose` and `--sample`.

```
Usage: prepare_multiqc.py [OPTIONS]

  Reads an input json from mutliqc and decomposes into individual samples
  and divides by analysis type. Essentially it is reading: raw_data from
  json file.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the level of log output.  [default:
                                  INFO]
  -m, --multiqc-json PATH         Input json file from multiqc run.
                                  multiqc_data.json  [required]
  -o, --output-json TEXT          Output json file name. If decompose is
                                  enabled, input
                                  %filename%.json will be
                                  considered as suffix.
                                  e.g.
                                  %samples%.%filename%.json.  [default:
                                  output.json]
  --decompose / --no-decompose    Decompose output for each sample.  [default:
                                  True]
  -s, --sample TEXT               Sample name to search within multiqc. This
                                  can be specified multiple times.
                                  This should
                                  be a exact match.
  --help                          Show this message and exit.
```

## Examples:

The following example will write three output files: `ACC5152A10_R.sample.json`, `ACC5152A1_R.sample.json`, and
`ACC5152A1_R_FR.sample.json`:

```
./prepare_multiqc.py \
    --multiqc-json multiqc_data.json \
    --output-json sample.json  \
    --log-level DEBUG \
    --decompose \
    --sample ACC5152A10_R \
    --sample ACC5152A1_R \
    --sample ACC5152A1_R_FR
```
