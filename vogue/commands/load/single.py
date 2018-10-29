import click

@click.command("single", short_help = "Read and load lims data")
@click.option(
    '-s',
    '--sample-id',
    required=True,
    help='Input sample id'
)
@click.option(
    "--load-sample/--no-load-sample",
    default=False,
    show_default=True,
    help=
    "Load from sample or not. (dry-run)",
)
@click.pass_context

def single(context, sample, load_sample):
    pass
