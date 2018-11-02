import click

@click.command("analysis", short_help = "Read files from analysis workflows")
@click.option(
    '-s',
    '--sample-id',
    required=True,
    help='Input sample id'
)
@click.pass_context

def analysis(context, sample_id):
    """
    Read and load analysis results. These are either QC or analysis output files.
    """
    pass
