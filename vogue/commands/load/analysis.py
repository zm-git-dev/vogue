import logging
import click
import yaml
import json

from flask.cli import with_appcontext, current_app

from vogue.tools.cli_utils import json_read
from vogue.tools.cli_utils import yaml_read
from vogue.tools.cli_utils import check_file
from vogue.build.analysis import validate_conf
from vogue.build.analysis import build_analysis
from vogue.tools.cli_utils import add_doc as doc
from vogue.load.analysis import load_analysis
import vogue.models.analysis as analysis_model

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


def concat_dict_keys(my_dict: dict, key_name="", out_key_list=list()):
    '''
    Recursively create a list of key:key1,key2 from a nested dictionary
    '''

    if isinstance(my_dict, dict):

        if key_name != "":
            out_key_list.append(key_name + ":" +
                                ", ".join(list(my_dict.keys())))

        for k in my_dict.keys():
            concat_dict_keys(my_dict[k], key_name=k, out_key_list=out_key_list)

    return out_key_list


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
    default=['all'],
    help='Type of analysis results to load.')
@click.option('--dry', is_flag=True, help='Load from sample or not. (dry-run)')
@doc(f"""
    Read and load analysis results. These are either QC or analysis output files.

    The inputs are unique ID with an analysis config file (JSON/YAML) which includes analysis results matching the
    analysis model. Analysis types recognize the following keys in the input file: {" ".join(concat_dict_keys(analysis_model.ANALYSIS_SETS,key_name=""))}
        """)
@with_appcontext
def analysis(sample_id, analysis_config, analysis_type):

    LOG.info("Reading and validating config file.")
    try:
        check_file(analysis_config)
    except FileNotFoundError as e:
        click.Abort()

    LOG.info("Trying JSON format")
    analysis_dict = json_read(analysis_config)
    if not isinstance(analysis_dict, dict):
        LOG.info("Trying YAML format")
        analysis_dict = yaml_read(analysis_config)
        if not isinstance(analysis_dict, dict):
            LOG.error("Cannot read input analysis config file. Type unknown.")
            click.Abort()

    LOG.info("Validating config file")
    valid_analysis = validate_conf(analysis_dict)
    if valid_analysis is None:
        LOG.error("Input config file is not valid.")
        click.Abort()

    ready_analysis = dict()
    if 'all' in analysis_type:
        for my_analysis in analysis_model.ANALYSIS_DESC.keys():
            tmp_analysis_dict = build_analysis(analysis_dict, my_analysis,
                                               valid_analysis, sample_id)
            if tmp_analysis_dict:
                ready_analysis = {**ready_analysis, **tmp_analysis_dict}
    else:
        for my_analysis in analysis_type:
            tmp_analysis_dict = build_analysis(analysis_dict, my_analysis,
                                               valid_analysis, sample_id)
            if tmp_analysis_dict:
                ready_analysis = {**ready_analysis, **tmp_analysis_dict}

    if ready_analysis:
        LOG.info(
            f'Values for {list(ready_analysis.keys())} loaded for sample {sample_id}'
        )
    else:
        LOG.warning(
            f'No enteries were found for the given analysis type: {analysis_type}'
        )

    load_analysis(adapter=current_app.adapter, analysis=ready_analysis)
