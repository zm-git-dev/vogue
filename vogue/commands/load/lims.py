import click
from vogue.load.sample import load_one_sample, dry_run, load_all_samples


@click.command("lims", short_help = "load lims into db.")
@click.option('-s', '--sample-lims-id', help = 'Input sample lims id')
@click.option('--load-all/--no-load-all', default = False, help = 'Loads all lims sample ids')
@click.option('--dry-run', is_flag=True, help='If dry run')
                help = 'Load from sample or not. (dry-run)')
@click.pass_context


def lims(context, sample_lims_id, dry, load_all):
    """Read and load lims data for a given sample id"""
    adapter = context.obj['adapter']
    if dry:
        click.echo(f"Dry run...bla bla\n {adapter.db}")
        if sample_lims_id:
            click.echo(f"Will build and load lims sample {sample_lims_id}:")
            dry_run(adapter, sample_lims_id)
        if load_all:
            click.echo(f"Will build and load all lims samples.")
        return

    if load_all:
        load_all_samples(adapter)
        return
  

    load_one_sample(adapter, sample_lims_id)
