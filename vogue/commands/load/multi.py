import click

@click.command("multi", short_help = "Read and load lims data")
@click.option(
    '-s',
    '--sample-ids',
    help='Input sample ids'
)
@click.option(
    "--build-all/--no-build-all",
    default=False,
    show_default=True,
    help=
    "Build from all samples found in lims database. WARNING: this loads EVERYTHING.",
)
@click.option(
    "--load-samples/--no-load-samples",
    default=False,
    show_default=True,
    help=
    "Load from samples or not. (dry-run)",
)
@click.pass_context

def multi(context, sample_ids, build_all, load_samples):
    pass
