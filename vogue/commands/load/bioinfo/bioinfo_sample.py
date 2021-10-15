"""
    Add or update analysis results for samples from bioinfo_processed into bioinf_sample collection
"""
import logging
import click


from vogue.tools.cli_utils import add_doc as doc
from vogue.build.bioinfo_analysis import build_bioinfo_sample
from vogue.load.bioinfo_analysis import load_analysis

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


@click.command(
    "sample",
    short_help="Process stats and results from bioinfo process and load sample into the bioinfo_sample collection.",
)
@click.option(
    "-c", "--analysis-case", help="The case to retrieve samples and load into bioinfo_sample."
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
    Load samples analysis results from bioinfo processed collection
    into bioinfo sample collection.
    """
)
@click.pass_context
def bioinfo_sample(ctx: click.Context, dry, analysis_case, load_all):
    adapter = ctx.obj["adapter"]

    if (not load_all and not analysis_case) or (load_all and analysis_case):
        LOG.error(
            "--load-all and --analysis-case are mutually exclusive and cannot be used together"
        )
        raise click.Abort()

    current_processed_analysis = adapter.bioinfo_processed(analysis_case)
    LOG.info(
        "Loading following samples to bioinfo_samples: %s",
        ", ".join(current_processed_analysis["samples"]),
    )

    for sample in current_processed_analysis["samples"]:
        sample_analysis = build_bioinfo_sample(
            analysis_dict=current_processed_analysis, process_case=True, sample_id=sample
        )
        load_res = load_analysis(
            adapter=adapter,
            lims_id=sample,
            processed=True,
            is_sample=True,
            dry_run=dry,
            analysis=sample_analysis,
        )
        if load_res:
            LOG.info("Sample %s is loaded into database", sample)
        else:
            LOG.warning("Loading failed for sample %s", sample)
