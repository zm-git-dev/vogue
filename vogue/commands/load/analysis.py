import logging
import click
import yaml
import json
from vogue.tools.cli_utils import json_read
from vogue.tools.cli_utils import yaml_read
from vogue.tools.cli_utils import check_file
from vogue.build.analysis import validate_conf
from vogue.build.analysis import build_analysis
import vogue.models.analysis as analysis_model

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.command("analysis", short_help="Read files from analysis workflows")
@click.option('-s', '--sample-id', required=True, help='Input sample id')
@click.option(
    '-a',
    '--analysis-config',
    type=click.Path(),
    required=True,
    help='Input config file. Accepted format: JSON, YAML')
@click.option(
    '-t',
    '--analysis-type',
    type=click.Choice(list(analysis_model.ANALYSIS_DESC.keys()) + ['all']),
    multiple=True,
    default='all',
    help='Type of analysis results to load.')
@click.pass_context
def analysis(context, sample_id, analysis_config, analysis_type):
    """
    Read and load analysis results. These are either QC or analysis output files.
    """
    LOG.info("Reading and validating config file.")
    try:
        check_file(analysis_config)
    except FileNotFoundError as e:
        context.abort()

    LOG.info("Trying JSON format")
    analysis_dict = json_read(analysis_config)
    if not isinstance(analysis_dict, dict):
        LOG.info("Trying YAML format")
        analysis_dict = yaml_read(analysis_config)
        if not isinstance(analysis_dict, dict):
            LOG.error("Cannot read input analysis config file. Type unknown.")
            context.abort()

    LOG.info("Validating config file")
    if not validate_conf(analysis_dict):
        LOG.error("Input config file is not valid format")
        context.abort()

    ready_analysis = dict()
    if analysis_type == 'all':
        for my_analysis in analysis_model.ANALYSIS_DESC.keys():
            tmp_analysis_dict = build_analysis(analysis_dict, my_analysis)
            if tmp_analysis_dict:
                ready_analysis = {**ready_analysis, **tmp_analysis_dict}
    else:
        for my_analysis in analysis_type:
            tmp_analysis_dict = build_analysis(analysis_dict, my_analysis)
            if tmp_analysis_dict:
                ready_analysis = {**ready_analysis, **tmp_analysis_dict}

    if ready_analysis:
        LOG.info(
            f'The following keys were found {list(ready_analysis.keys())}')
    else:
        LOG.warning(
            f'No enteries were found for the given analysis type: {analysis_type}'
        )
