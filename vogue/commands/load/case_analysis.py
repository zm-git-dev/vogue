import logging
import copy
import click

from flask.cli import with_appcontext, current_app
from flask import abort as flaskabort

from vogue.tools.cli_utils import json_read
from vogue.tools.cli_utils import dict_replace_dot
from vogue.tools.cli_utils import yaml_read
from vogue.tools.cli_utils import check_file
from vogue.tools.cli_utils import concat_dict_keys
from vogue.build.case_analysis import build_analysis
from vogue.tools.cli_utils import add_doc as doc
from vogue.load.case_analysis import load_analysis
from vogue.parse.load.case_analysis import validate_conf
import vogue.models.case_analysis as analysis_model

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.command("analysis", short_help="Read files from analysis workflows")
@click.option('-s',
              '--sample-id',
              required=True,
              multiple=True,
              help='Input sample id.')
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
@click.option('-c',
              '--analysis-case',
              required=True,
              help='''The case that this sample belongs.
        It can be specified multiple times.''')
@click.option('-w',
              '--analysis-workflow',
              required=True,
              help='Analysis workflow used.')
@click.option('--workflow-version',
              required=True,
              help='Analysis workflow used.')
@click.option('--is-case',
              is_flag=True,
              help='Specify this flag if input json is case level.')
@click.option('--case-analysis-type',
              type=click.Choice(['multiqc', 'custom']),
              default='multiqc',
              help='Specify the type for the case analysis. i.e. if it is multiqc output, then choose multiqc')
@click.option('--dry', is_flag=True, help='Load from sample or not. (dry-run)')
@doc(f"""
    Read and load analysis results. These are either QC or analysis output files.

    The inputs are unique ID with an analysis config file (JSON/YAML) which includes analysis results matching the
    analysis model. Analysis types recognize the following keys in the input file: {" ".join(concat_dict_keys(analysis_model.ANALYSIS_SETS,key_name=""))}
        """)
@with_appcontext
def analysis(sample_id, dry, analysis_config, analysis_type, analysis_case,
             analysis_workflow, workflow_version, is_case, case_analysis_type):

    # is_case does not work with multiple input analysis configs
    if is_case and len(analysis_config) > 1:
        LOG.error("is_case flag cannot be used with multiple input files")
        raise click.Abort()

    if is_case and not case_analysis_type:
        LOG.error("is_case flag requires a case_analysis_type value")
        raise click.Abort()

    if not is_case and len(sample_id) > 1:
        LOG.error("for standard input, only use single sample ids.")
        raise click.Abort()

    if not is_case:
        sample_id = copy.deepcopy(sample_id[0])

    analysis_dict = dict()

    #if is_case flag is enabled, build dictionary without merging.
    # Loop over list of input config files for single sample and merge them into
    # one single dictionary
    for input_config in analysis_config:

        LOG.info("Reading and validating config file: %s", input_config)
        try:
            check_file(input_config)
        except FileNotFoundError:
            raise click.Abort()

        LOG.info("Trying JSON format")
        tmp_analysis_dict = json_read(input_config)

        if not isinstance(analysis_dict, dict):
            LOG.info("Trying YAML format")
            tmp_analysis_dict = yaml_read(input_config)
            if not isinstance(tmp_analysis_dict, dict):
                LOG.error(
                    "Cannot read input analysis config file. Type unknown.")
                raise click.Abort()

        analysis_dict = {**analysis_dict, **tmp_analysis_dict}

    analysis_dict = dict_replace_dot(analysis_dict)

    if not is_case:
        LOG.info("Validating parsed config file(s).")
        valid_analysis = validate_conf(analysis_dict)
        if valid_analysis is None:
            LOG.error("Invalid or badly formatted file(s).")
            raise click.Abort()
    else:
        old_keys = list(analysis_dict.keys())
        analysis_dict[case_analysis_type] = copy.deepcopy(analysis_dict)
        valid_analysis = dict()
        for key in old_keys:
            analysis_dict.pop(key)

    analysis_dict['case'] = analysis_case
    analysis_dict['workflow'] = analysis_workflow
    analysis_dict['workflow_version'] = workflow_version
    analysis_dict['sample'] = sample_id

    # Get current sample if any
    if not is_case:
        current_analysis = current_app.adapter.sample_analysis(sample_id)
    else:
        current_analysis = current_app.adapter.case_analysis(analysis_case)

    ready_analysis = build_analysis(analysis_dict=analysis_dict,
                                    analysis_type=analysis_type,
                                    valid_analysis=valid_analysis,
                                    current_analysis=current_analysis,
                                    case_analysis_type=case_analysis_type,
                                    build_case=is_case)

    if ready_analysis and not is_case:
        LOG.info('Values for %s  loaded for sample %s',
                 list(ready_analysis.keys()), sample_id)
    elif not ready_analysis and not is_case:
        LOG.warning('No enteries were found for the given analysis type: %s',
                    analysis_type)
    else:
        LOG.info('Case %s will be added/updated', analysis_case)

    load_analysis(adapter=current_app.adapter,
                  lims_id=sample_id,
                  is_case=is_case,
                  dry_run=dry,
                  analysis=ready_analysis)
