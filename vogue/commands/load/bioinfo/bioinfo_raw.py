"""
    Add or update bioinfo results to bioinfo raw collection
"""
import logging
import copy
import click


from vogue.tools.cli_utils import json_read
from vogue.tools.cli_utils import dict_replace_dot
from vogue.tools.cli_utils import yaml_read
from vogue.tools.cli_utils import check_file
from vogue.tools.cli_utils import concat_dict_keys
from vogue.tools.cli_utils import add_doc as doc
from vogue.build.bioinfo_analysis import build_analysis
from vogue.load.bioinfo_analysis import load_analysis
import vogue.models.bioinfo_analysis as analysis_model

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


@click.command(
    "raw", short_help="Read files from analysis workflows and laods in bioinfo_raw collection."
)
@click.option(
    "--sample-list",
    help="""Input list of comma separated sample names. Or specify it
within input results file under "samples" key.""",
)
@click.option(
    "-a",
    "--analysis-result",
    type=click.Path(),
    multiple=True,
    help="Input file for bioinfo analysis results. Accepted format: JSON, YAML",
)
@click.option(
    "-t",
    "--analysis-type",
    type=click.Choice(list(analysis_model.ANALYSIS_DESC.keys()) + ["all"]),
    multiple=True,
    default=["all"],
    help="Type of analysis results to load.",
)
@click.option(
    "-c",
    "--analysis-case",
    required=True,
    help="""The case that this sample belongs.
        It can be specified multiple times.""",
)
@click.option(
    "-w",
    "--analysis-workflow",
    type=click.Choice(["mip-dna", "balsamic", "microsalt"]),
    required=True,
    help="Analysis workflow used.",
)
@click.option("--workflow-version", required=True, help="Analysis workflow used.")
@click.option(
    "--case-analysis-type",
    type=click.Choice(["multiqc", "microsalt", "custom"]),
    default="multiqc",
    help="Specify the type for the case analysis. i.e. if it is multiqc output, then choose multiqc",
)
@click.option("--dry", is_flag=True, help="Load from sample or not. (dry-run)")
@doc(
    f"""
    Read and load analysis results. These are either QC or analysis output files.

    The inputs are unique ID with an analysis config file (JSON/YAML) which includes analysis results matching the
    analysis model. Analysis types recognize the following keys in the input file: {" ".join(concat_dict_keys(analysis_model.ANALYSIS_SETS,key_name=""))}
        """
)
@click.pass_context
def bioinfo_raw(
    ctx: click.Context,
    dry,
    analysis_result,
    analysis_type,
    analysis_case,
    analysis_workflow,
    workflow_version,
    case_analysis_type,
    sample_list,
):
    adapter = ctx.obj["adapter"]

    analysis_dict = dict()

    # if is_case flag is enabled, build dictionary without merging.
    # Loop over list of input config files for single sample and merge them into
    # one single dictionary

    for input_config in analysis_result:

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
                LOG.error("Cannot read input analysis config file. Type unknown.")
                raise click.Abort()

        analysis_dict = {**analysis_dict, **tmp_analysis_dict}

    analysis_dict = dict_replace_dot(analysis_dict)

    if case_analysis_type == "multiqc":
        LOG.info("--case-analysis-type set to multiqc, taking only report_saved_raw_data key")
        report_saved_raw_data = analysis_dict["report_saved_raw_data"]
        analysis_dict.clear()
        analysis_dict["report_saved_raw_data"] = copy.deepcopy(report_saved_raw_data)

    # Get current sample if any
    old_keys = list(analysis_dict.keys())
    analysis_dict[case_analysis_type] = copy.deepcopy(analysis_dict)
    for key in old_keys:
        analysis_dict.pop(key)

    valid_analysis = dict()
    analysis_dict["case"] = analysis_case
    analysis_dict["workflow"] = analysis_workflow
    analysis_dict["workflow_version"] = workflow_version
    analysis_dict["case_analysis_type"] = case_analysis_type

    if sample_list:
        sample_id = sample_list.split(",")
    else:
        if "sample" not in analysis_dict.keys():
            LOG.error("sample key not found in input json. Use --sample-list instead")
            raise click.Abort()
        # store sample_id from dict to avoid losing it downstream cleanup
        sample_id = analysis_dict["sample"]

    analysis_dict["sample"] = sample_id
    # Don't process the case
    current_analysis = adapter.bioinfo_raw(analysis_case)

    # Don't process the case
    ready_analysis = build_analysis(
        analysis_dict=analysis_dict,
        analysis_type=analysis_type,
        valid_analysis=valid_analysis,
        current_analysis=current_analysis,
        process_case=False,
        cleanup=False,
    )

    if ready_analysis:
        LOG.info("Values for %s  loaded for case %s", list(ready_analysis.keys()), analysis_case)
        LOG.info("Loaded samples in case are: %s", ", ".join(ready_analysis["samples"]))

    else:
        LOG.warning("No enteries were found for the given analysis type: %s", analysis_type)
    LOG.info("Case %s will be added/updated", analysis_case)

    load_analysis(
        adapter=adapter,
        lims_id=analysis_dict["sample"],
        processed=False,
        is_sample=False,
        dry_run=dry,
        analysis=ready_analysis,
    )
