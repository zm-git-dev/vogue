"""
    Functionality to add or update to processed bioinfo collection
"""
import logging
import copy
import click


from vogue.tools.cli_utils import concat_dict_keys
from vogue.tools.cli_utils import add_doc as doc
from vogue.tools.cli_utils import recursive_default_dict
from vogue.tools.cli_utils import convert_defaultdict_to_regular_dict
from vogue.build.bioinfo_analysis import build_analysis
from vogue.load.bioinfo_analysis import load_analysis
from vogue.parse.load.bioinfo_analysis import inspect_analysis_result
import vogue.models.bioinfo_analysis as analysis_model

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


@click.command(
    "process",
    short_help="""Process stats and result from bioinfo raw and load into the bioinfo_processed collection. """,
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
    "--cleanup/--not-cleanup",
    is_flag=True,
    help="Specify this flag if input json should be cleanup based on analysis-type and models.",
)
@click.option(
    "--case-analysis-type",
    type=click.Choice(["multiqc", "microsalt", "custom"]),
    default="multiqc",
    help="Specify the type for the case analysis. i.e. if it is multiqc output, then choose multiqc",
)
@click.option(
    "-a",
    "--load-all",
    is_flag=True,
    help="Load all samples for all cases within bioinfo_processed.",
)
@click.option("--dry", is_flag=True, help="Load from sample or not. (dry-run)")
@doc(
    f"""
    Load bioinfo analysis results from bioinfo_raw collection into bioinfo_processed 

    Analysis types recognize the following keys in the input file: {" ".join(concat_dict_keys(analysis_model.ANALYSIS_SETS,key_name=""))}
        """
)
@click.pass_context
def bioinfo_process(
    ctx: click.Context,
    dry,
    analysis_type,
    analysis_case,
    analysis_workflow,
    workflow_version,
    case_analysis_type,
    cleanup,
    load_all,
):
    adapter = ctx.obj["adapter"]

    if (not load_all and not analysis_case) or (load_all and analysis_case):
        LOG.error(
            "--load-all and --analysis-case are mutually exclusive and cannot be used together"
        )
        raise click.Abort()
    analysis_dict = dict()

    # if is_case flag is enabled, build dictionary without merging.
    # Loop over list of input config files for single sample and merge them into
    # one single dictionary

    valid_analysis = dict()
    analysis_dict["case"] = analysis_case
    analysis_dict["workflow"] = analysis_workflow
    analysis_dict["workflow_version"] = workflow_version
    analysis_dict["case_analysis_type"] = case_analysis_type

    current_analysis = adapter.bioinfo_raw(analysis_case)

    if current_analysis is None:
        LOG.info("Raw import for this case does not exist. Load it without processed flag first")
        raise click.Abort()

    if not case_analysis_type in current_analysis["case_analysis_types"]:
        LOG.info("%s doesn't exist for case %s", case_analysis_type, analysis_case)
        raise click.Abort()

    analysis_dict[case_analysis_type] = current_analysis[analysis_workflow][case_analysis_type][-1]

    analysis_dict["sample"] = current_analysis["samples"]
    # if case analysis type is microsalt, aggregate samples under analysis result keys
    # e.g. {'smpl_1': {'key':'value_smpl1'}, 'smpl_2': {'key':'value_smpl2'}}
    # will be converted to {'key': {'smpl_1':'value_smpl1', 'smpl_2': 'value_smpl2'}}
    if case_analysis_type == "microsalt":
        new_analysis_dict = recursive_default_dict()
        for key in analysis_dict["microsalt"].keys():
            if key in analysis_dict["sample"]:
                for next_key, next_value in analysis_dict["microsalt"][key].items():
                    new_analysis_dict[next_key] = {
                        **new_analysis_dict[next_key],
                        **{key: next_value},
                    }
        analysis_dict.pop("microsalt")
        tmp_dict = convert_defaultdict_to_regular_dict(new_analysis_dict)
        analysis_dict["microsalt"] = copy.deepcopy(tmp_dict)

    if cleanup:
        LOG.info("Validating parsed config file(s).")
        valid_analysis = inspect_analysis_result(analysis_dict)
        if valid_analysis is None:
            LOG.error("Invalid or badly formatted file(s).")
            raise click.Abort()

    current_analysis = adapter.bioinfo_processed(analysis_case)

    # Don't process the case
    ready_analysis = build_analysis(
        analysis_dict=analysis_dict,
        analysis_type=analysis_type,
        valid_analysis=valid_analysis,
        current_analysis=current_analysis,
        process_case=True,
        cleanup=cleanup,
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
        processed=True,
        is_sample=False,
        dry_run=dry,
        analysis=ready_analysis,
    )
