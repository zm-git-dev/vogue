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
import os
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
        # If any sample is provided:
        if samples:
            # Looping through provided sampels:
            for sample in samples:
                # Since this is for decompose, samples will be first keys.
                analysis[sample] = dict()
                # Loop through valid keys found
                for key in json_keys:
                    # If this particular sample is within this key (multiqc module)
                    if sample in multiqc_dict[key].keys():
                        LOG.debug("Found %s in %s analysis", sample, key)
                        # Store valid key content (multiqc module) in sample key of output dict
                        analysis[sample][key] = multiqc_dict[key][sample]
        else:
            for common_key in json_keys:
                analysis[common_key] = multiqc_dict["report_saved_raw_data"][
                    common_key]

    return analysis


def write_json(multiqc_dict, json_out, out_dir):
    """
    Input: a multiqc dictionary
    Output: output json filename
    """
    try:
        with open(os.path.join(out_dir, json_out), "w") as file_out:
            json.dump(multiqc_dict, file_out, indent=4)
    except OSError:
        raise click.Abort("Write failed")


def write_json_per_sample(multiqc_dict, json_out_suffix, out_dir):
    """
    Input: a multiqc dictionary with samples as first key
    Output: multiple output files with json_out_suffix.
    """
    try:
        for sample in multiqc_dict.keys():
            fname = sample + "." + json_out_suffix
            fname = os.path.join(out_dir, fname)
            LOG.debug("Writing output file for %s: %s", sample, fname)
            with open(fname, "w") as file_out:
                json.dump(multiqc_dict[sample], file_out, indent=4)
    except OSError:
        raise click.Abort("Write failed")


@click.command()
@click.option('--log-level',
              default='DEBUG',
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
@click.option('-d',
              '--directory',
              default=os.getcwd(),
              show_default=True,
              help='Working directory for output file(s).')
@click.option('--decompose/--no-decompose',
              default=True,
              show_default=True,
              help='Decompose output for each sample.')
@click.option('--regex-match/--no-regex-match',
              default=False,
              show_default=True,
              help='Regex match sample name within multiqc.')
@click.option('-s',
              '--sample',
              multiple=True,
              help="""
        Sample name to search within multiqc. This can be specified multiple times.
        This should be a exact match.
        """)
def prepare_multiqc(multiqc_json, log_level, output_json, decompose, sample,
                    directory, regex_match):
    """
    Reads an input json from mutliqc and decomposes into individual samples
    and divides by analysis type. Essentially it is reading: raw_data from
    json file.
    """
    coloredlogs.install(level=log_level)

    LOG.info("Running version %s", __version__)
    LOG.debug("Debug logging enabled.")

    if decompose:
        LOG.debug("Output decompose is enabled.")

    if decompose and not sample:
        LOG.error(
            "Decompose mode needs list of samples. Choose one from above.")
        raise click.Abort()

    LOG.info("Reading input multiqc json files: %s", multiqc_json)

    multiqc_dict = read_multiqc(multiqc_json)

    LOG.debug("Validating input json.")

    if validate_multiqc(multiqc_dict):
        LOG.info("Input json file is a valid multiqc")
        multiqc_dict = extract_analysis(multiqc_dict=multiqc_dict,
                                        json_keys="all")
    else:
        LOG.error("Input json does not seem to be a valid multiqc json")
        raise click.Abort()

    # Match multiqc_dict keys with the analysis_type of ANALYSIS_SETS
    analysis_common_keys = list()
    for key in multiqc_dict.keys():
        if key in list(ANALYSIS_SETS.keys()):
            analysis_common_keys.append(key)

    LOG.info("Found following modules in json: %s", analysis_common_keys)

    # Find samples within valid multiqc report samples
    samples_in_multiqc = list()
    for key in analysis_common_keys:
        samples_in_multiqc.extend(list(multiqc_dict[key].keys()))
    samples_in_multiqc = list(set(samples_in_multiqc))
    LOG.info("Found following samples in valid modules: %s",
             samples_in_multiqc)

    # Find valid samples in input
    if sample:
        valid_samples = list()
        if regex_match:
            LOG.warning("Regex sample match is enabled.")
            for check_sample in sample:
                for sample_found in samples_in_multiqc:
                    if sample_found.startswith(check_sample):
                        LOG.debug(
                            "Matched sample %s with %s in multiqc report",
                            check_sample, sample_found)
                        valid_samples.append(sample_found)
        else:
            LOG.info("Using exact match for sample names.")
            for check_sample in sample:
                if check_sample in samples_in_multiqc:
                    valid_samples.append(check_sample)
        LOG.info("Found the following valid samples in valid modules: %s",
                 valid_samples)

    if decompose:
        for check_sample in sample:
            if check_sample not in samples_in_multiqc and not regex_match:
                LOG.warning("%s was not found in multiqc report", check_sample)
        if not valid_samples:
            LOG.error("None of the samples were found in multiqc report.")
            raise click.Abort()
        LOG.info("Decompose mode enabled.")
        LOG.info("Only the following samples will be processed: %s",
                 valid_samples)
        LOG.info("Only the following modules will be extracted: %s",
                 analysis_common_keys)
        multiqc_dict = extract_analysis(multiqc_dict=multiqc_dict,
                                        json_keys=analysis_common_keys,
                                        samples=valid_samples)
        write_json_per_sample(multiqc_dict, output_json, directory)

    else:
        LOG.info("Writing output file: %s", output_json)
        write_json(multiqc_dict, output_json, directory)


if __name__ == '__main__':
    prepare_multiqc()
