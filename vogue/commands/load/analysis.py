import logging
import click

from flask.cli import with_appcontext, current_app

from vogue.tools.cli_utils import json_read
from vogue.tools.cli_utils import yaml_read
from vogue.tools.cli_utils import check_file
from vogue.tools.cli_utils import concat_dict_keys
from vogue.build.analysis import build_analysis
from vogue.tools.cli_utils import add_doc as doc
from vogue.load.analysis import load_analysis
from vogue.parse.analysis import validate_conf
import vogue.models.analysis as analysis_model

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.command("analysis", short_help="Read files from analysis workflows")
@click.option('-s', '--sample-id', required=True, help='Input sample id')
@click.option('-a',
              '--analysis-config',
              type=click.Path(),
              multiple=True,
              required=True,
              help='Input config file. Accepted format: JSON, YAML')
@click.option(
    '-t',
    '--analysis-type',
    type=click.Choice(list(analysis_model.ANALYSIS_DESC.keys()) + ['all']),
    multiple=True,
    default=['all'],
    help='Type of analysis results to load.')
@click.option(
    '-c',
    '--analysis-case',
    required=True,
    help=
    'The case that this sample belongs to. It can be specified multiple times.'
)
@click.option('-w',
              '--analysis-workflow',
              required=True,
              help='Analysis workflow used.')
@click.option('--workflow-version',
              required=True,
              help='Analysis workflow used.')
@click.option('--dry', is_flag=True, help='Load from sample or not. (dry-run)')
@doc(f"""
    Read and load analysis results. These are either QC or analysis output files.

    The inputs are unique ID with an analysis config file (JSON/YAML) which includes analysis results matching the
    analysis model. Analysis types recognize the following keys in the input file: {" ".join(concat_dict_keys(analysis_model.ANALYSIS_SETS,key_name=""))}
        """)
@with_appcontext
def analysis(sample_id, dry, analysis_config, analysis_type, analysis_case,
             analysis_workflow, workflow_version):

    analysis_dict = dict()
    # Loop over list of input config files for single sample and merge them into
    # one single dictionary
    for input_config in analysis_config:

        LOG.info("Reading and validating config file: %s", input_config)
        try:
            check_file(input_config)
        except FileNotFoundError:
            click.Abort()

        LOG.info("Trying JSON format")
        tmp_analysis_dict = json_read(input_config)

        if not isinstance(analysis_dict, dict):
            LOG.info("Trying YAML format")
            tmp_analysis_dict = yaml_read(input_config)
            if not isinstance(tmp_analysis_dict, dict):
                LOG.error(
                    "Cannot read input analysis config file. Type unknown.")
                click.Abort()

        analysis_dict = {**analysis_dict, **tmp_analysis_dict}

    LOG.info("Validating parsed config file(s).")
    valid_analysis = validate_conf(analysis_dict)
    if valid_analysis is None:
        LOG.error("Invalid or badly formatted file(s).")
        click.Abort()

    analysis_dict['case'] = analysis_case
    analysis_dict['workflow'] = analysis_workflow
    analysis_dict['workflow_version'] = workflow_version

    # Get current sample if any
    current_analysis = current_app.adapter.analysis(sample_id)

    ready_analysis = build_analysis(analysis_dict=analysis_dict,
                                    analysis_type=analysis_type,
                                    valid_analysis=valid_analysis,
                                    sample_id=sample_id,
                                    current_analysis=current_analysis)

    if ready_analysis:
        LOG.info(
            'Values for %s  loaded for sample %s', list(ready_analysis.keys()), sample_id
        )
    else:
        LOG.warning(
            'No enteries were found for the given analysis type: %s', analysis_type
        )

    load_analysis(adapter=current_app.adapter,
                  lims_id=sample_id,
                  dry_run=dry,
                  analysis=ready_analysis)
