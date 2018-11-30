import logging

import click

import yaml
import json

from vogue.tools.cli_utils import json_read, yaml_read, check_file

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

def validate_conf(analysis_conf):
    """
    Takes input analysis_conf dictionary and validates entries.
    """
    return True

@click.command("analysis", short_help = "Read files from analysis workflows")
@click.option(
    '-s',
    '--sample-id',
    required=True,
    help='Input sample id'
)
@click.option(
    '-a',
    '--analysis-config',
    type=click.Path(),
    required=True,
    help='Input config file. Accepted format: JSON, YAML')
@click.pass_context

def analysis(context, sample_id, analysis_config):
    """
    Read and load analysis results. These are either QC or analysis output files.
    """
    LOG.info("Reading and validating config file.")
    check_file(analysis_config)
    LOG.info("Trying JSON format")
    analysis_dict = json_read(analysis_config)
    if not isinstance(analysis_dict,dict):
        LOG.info("Trying YAML format")
        analysis_dict = yaml_read(analysis_config)
        if not isinstance(analysis_dict,dict):
            LOG.error("Cannot read input analysis config file. Type unknown.")
            raise TypeError

    LOG.info("Validating config file")
    if not validate_conf(analysis_dict):
        LOG.error("Input config file is not valid format")
        raise TypeError
