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
from vogue.tools.cli_utils import add_doc as doc
from vogue.tools.cli_utils import recursive_default_dict
from vogue.tools.cli_utils import convert_defaultdict_to_regular_dict
from vogue.build.case_analysis import build_analysis
from vogue.load.case_analysis import load_analysis
from vogue.parse.load.case_analysis import validate_conf
import vogue.models.case_analysis as analysis_model

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.command("analysis", short_help="Read files from analysis workflows")
@click.option('--sample-list',
              help='Input list of comma separated sample names.')
@click.option('-a',
              '--analysis-config',
              type=click.Path(),
              multiple=True,
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
@click.option(
    '--processed/--not-processed',
    is_flag=True,
    help=
    'Specify this flag if input json should be processed and to be added to bioinfo_processed.'
)
@click.option(
    '--cleanup/--not-cleanup',
    is_flag=True,
    help=
    'Specify this flag if input json should be cleanup based on analysis-type and models.'
)
@click.option('--load-sample/--not-load-sample',
              is_flag=True,
              default=True,
              help='Specify this flag if ')
@click.option(
    '--case-analysis-type',
    type=click.Choice(['multiqc', 'microsalt', 'custom']),
    default='multiqc',
    help=
    'Specify the type for the case analysis. i.e. if it is multiqc output, then choose multiqc'
)
@click.option('--dry', is_flag=True, help='Load from sample or not. (dry-run)')
@doc(f"""
    Read and load analysis results. These are either QC or analysis output files.

    The inputs are unique ID with an analysis config file (JSON/YAML) which includes analysis results matching the
    analysis model. Analysis types recognize the following keys in the input file: {" ".join(concat_dict_keys(analysis_model.ANALYSIS_SETS,key_name=""))}
        """)
@with_appcontext
def analysis(dry, analysis_config, analysis_type, analysis_case,
             analysis_workflow, workflow_version, processed,
             case_analysis_type, sample_list, cleanup, load_sample):

    if not analysis_config and not processed:
        LOG.error('Either --analysis-config or --processed should be provided')
        raise click.Abort()

    analysis_dict = dict()

    if sample_list:
        sample_id = sample_list.split(',')
    else:
        if 'sample' not in analysis_dict.keys():
            LOG.error(
                'sample key not found in input json. Use --sample-list instead'
            )
            raise click.Abort()
        # store sample_id from dict to avoid losing it downstream cleanup
        sample_id = analysis_dict['sample']

    #if is_case flag is enabled, build dictionary without merging.
    # Loop over list of input config files for single sample and merge them into
    # one single dictionary

    if not processed and analysis_config:
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
                        "Cannot read input analysis config file. Type unknown."
                    )
                    raise click.Abort()

            analysis_dict = {**analysis_dict, **tmp_analysis_dict}

        analysis_dict = dict_replace_dot(analysis_dict)

        # Get current sample if any
        old_keys = list(analysis_dict.keys())
        analysis_dict[case_analysis_type] = copy.deepcopy(analysis_dict)
        for key in old_keys:
            analysis_dict.pop(key)

    valid_analysis = dict()
    analysis_dict['case'] = analysis_case
    analysis_dict['workflow'] = analysis_workflow
    analysis_dict['workflow_version'] = workflow_version
    analysis_dict['sample'] = sample_id
    analysis_dict['case_analysis_type'] = case_analysis_type

    if processed:
        current_analysis = current_app.adapter.bioinfo_raw(analysis_case)

        if current_analysis is None:
            LOG.info(
                "Raw import for this case does not exist. Load it without processed flag first"
            )
            raise click.Abort()
        elif not case_analysis_type in current_analysis['case_analysis_types']:
            LOG.info("%s doesn't exist for case %s", case_analysis_type,
                     analysis_case)
            raise click.Abort()

        analysis_dict[case_analysis_type] = current_analysis[
            analysis_workflow][case_analysis_type][-1]

        # if case analysis type is microsalt, aggregate samples under analysis result keys
        # e.g. {'smpl_1': {'key':'value_smpl1'}, 'smpl_2': {'key':'value_smpl2'}}
        # will be converted to {'key': {'smpl_1':'value_smpl1', 'smpl_2': 'value_smpl2'}}
        if case_analysis_type == "microsalt":
            new_analysis_dict = recursive_default_dict()
            for key in analysis_dict["microsalt"].keys():
                if key in analysis_dict['sample']:
                    for next_key, next_value in analysis_dict["microsalt"][key].items():
                        new_analysis_dict[next_key] = {**new_analysis_dict[next_key], **{key: next_value}}
            analysis_dict.pop("microsalt")
            tmp_dict = convert_defaultdict_to_regular_dict(new_analysis_dict)
            analysis_dict["microsalt"] = copy.deepcopy(tmp_dict)

        if cleanup:
            LOG.info("Validating parsed config file(s).")
            valid_analysis = validate_conf(analysis_dict)
            if valid_analysis is None:
                LOG.error("Invalid or badly formatted file(s).")
                raise click.Abort()

        current_analysis = current_app.adapter.bioinfo_processed(analysis_case)

        if load_sample:
            LOG.info("Loading following samples to bioinfo_samples: %s",
                     ", ".join(analysis_dict['sample']))
    else:

        # Don't process the case
        current_analysis = current_app.adapter.bioinfo_raw(analysis_case)
        processed = False
        cleanup = False

    # Don't process the case
    ready_analysis = build_analysis(analysis_dict=analysis_dict,
                                    analysis_type=analysis_type,
                                    valid_analysis=valid_analysis,
                                    current_analysis=current_analysis,
                                    process_case=processed,
                                    cleanup=cleanup)

    if ready_analysis:
        LOG.info('Values for %s  loaded for sample %s',
                 list(ready_analysis.keys()), sample_id)
    else:
        LOG.warning('No enteries were found for the given analysis type: %s',
                    analysis_type)
    LOG.info('Case %s will be added/updated', analysis_case)

    load_analysis(adapter=current_app.adapter,
                  lims_id=sample_id,
                  processed=processed,
                  dry_run=dry,
                  analysis=ready_analysis)
