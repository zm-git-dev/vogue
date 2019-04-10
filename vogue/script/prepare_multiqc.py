#!/usr/bin/env python
"""
# Copyright (c) Hassan Foroughi <hassan.foroughi@scilifelab.s>
#
# This module is free software. You can redistribute it and/or modify it under
# the terms of the MIT License, see the file COPYING included with this
# distribution.
#
# A simple script to decompose multiqc results
"""
import json
import logging
import click
import coloredlogs

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

__version__ = 0.01

ANALYSIS_SETS = {
    'multiqc_picard_dups':
    'multiqc json/yaml report key for picard mark duplicate.',
    'multiqc_picard_HsMetrics':
    'multiqc json/yaml report key for picard collecthsmetrics.',
    'multiqc_picard_AlignmentSummaryMetrics':
    'multiqc json/yaml report key for picard alignment summary metrics',
    'multiqc_picard_insertSize':
    'multiqc json/yaml report key for picard insert size metrics'
}


def read_multiqc(json_in):
    """
    Input: json file path
    Output: A dictionary of input json
    """

    with open(json_in, "r") as myfile:
        multiqc_out = json.load(myfile)

    return multiqc_out


def validate_multiqc(multiqc_dict):
    """
    Input: dictionary of multiqc results
    Output: True if dictionary is a valid multiqc result.
            i.e. includes report_saved_raw_data key
    """

    valid_multiqc = False

    if "report_saved_raw_data" in list(multiqc_dict.keys()):
        valid_multiqc = True

    return valid_multiqc


def extract_analysis(multiqc_dict, json_keys="all", samples=tuple()):
    """
    Input: dictionary of multiqc results
    Output: enteries under report_saved_raw_data
    """

    analysis = dict()
    if json_keys == "all":
        analysis = multiqc_dict["report_saved_raw_data"]
    else:
        if samples:
            for sample in samples:
                # Since this is for decompose, samples will be first keys.
                analysis[sample] = dict()
                for key in json_keys:
                    if sample in multiqc_dict[key].keys():
                        LOG.debug("Found %s in %s analysis", sample, key)
                        analysis[sample][key] = multiqc_dict[key][sample]
        else:
            for common_key in json_keys:
                analysis[common_key] = multiqc_dict["report_saved_raw_data"][
                    common_key]

    return analysis


def write_json(multiqc_dict, json_out):
    """
    Input: a multiqc dictionary
    Output: output json filename
    """
    try:
        with open(json_out, "w") as file_out:
            json.dump(multiqc_dict, file_out, indent=4)
    except OSError:
        raise click.Abort("Write failed")


def write_json_per_sample(multiqc_dict, json_out_suffix):
    """
    Input: a multiqc dictionary with samples as first key
    Output: multiple output files with json_out_suffix.
    """
    try:
        for sample in multiqc_dict.keys():
            fname = sample + "." + json_out_suffix
            LOG.debug("Writing output file for %s: %s", sample, fname)
            with open(fname, "w") as file_out:
                json.dump(multiqc_dict[sample], file_out, indent=4)
    except OSError:
        raise click.Abort("Write failed")


@click.command()
@click.option('--log-level',
              default='INFO',
              type=click.Choice(LOG_LEVELS),
              help="Set the level of log output.",
              show_default=True)
@click.option('-m',
              '--multiqc-json',
              required=True,
              type=click.Path(),
              help='Input json file from multiqc run. multiqc_data.json')
@click.option('-o',
              '--output-json',
              default="output.json",
              show_default=True,
              help="""
        Output json file name. If decompose is enabled, input
        %filename%.json will be considered as suffix.
        e.g. %samples%.%filename%.json.
        """)
@click.option('--decompose/--no-decompose',
              default=True,
              show_default=True,
              help='Decompose output for each sample.')
@click.option('-s',
              '--sample',
              multiple=True,
              help="""
        Sample name to search within multiqc. This can be specified multiple times.
        This should be a exact match.
        """)
def prepare_multiqc(multiqc_json, log_level, output_json, decompose, sample):
    """
    Reads an input json from mutliqc and decomposes into individual samples
    and divides by analysis type. Essentially it is reading: raw_data from
    json file.
    """
    coloredlogs.install(level=log_level)

    LOG.info("Running version %s", __version__)
    LOG.debug("Debug logging enabled.")
    LOG.info("Reading input multiqc json files: %s", multiqc_json)

    multiqc_dict = read_multiqc(multiqc_json)

    LOG.debug("Output decompose is enabled.")
    LOG.debug("Validating input json.")

    if validate_multiqc(multiqc_dict):
        LOG.info("Input json file is a valid multiqc")
        multiqc_dict = extract_analysis(multiqc_dict=multiqc_dict,
                                        json_keys="all")
    else:
        LOG.error("Input json does not seem to be a valid multiqc json")
        raise click.Abort()

    # Match multiqc_dict keys with the analysis_type of ANALYSIS_SETS
    analysis_common_keys = [
        e for e in multiqc_dict.keys() if e in list(ANALYSIS_SETS.keys())
    ]

    samples_found = list(
        set([
            s for key in analysis_common_keys
            for s in multiqc_dict[key].keys()
        ]))

    if decompose:
        LOG.info("Decompose mode enabled.")
        LOG.info("Found following modules in json: %s", multiqc_dict.keys())
        LOG.info("Only the following modules will be extracted: %s",
                 analysis_common_keys)
        LOG.info("Found following samples in valid modules: %s", samples_found)
        if not sample:
            LOG.error(
                "Decompose mode needs list of samples. Choose one from above.")
            raise click.Abort()
        if sample:
            LOG.info("Preparing output only for sample(s) %s", sample)
            multiqc_dict = extract_analysis(multiqc_dict=multiqc_dict,
                                            json_keys=analysis_common_keys,
                                            samples=sample)
        write_json_per_sample(multiqc_dict, output_json)

    else:
        LOG.info("Writing output file: %s", output_json)
        write_json(multiqc_dict, output_json)


if __name__ == '__main__':
    prepare_multiqc()
