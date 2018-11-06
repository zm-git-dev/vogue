import click
from vogue.load.sample import load_lims_sample, dry_run, load_all_samples


@click.command("lims", short_help = "load lims into db.")
@click.option('-s', '--sample-lims-id', help = 'Input sample lims id')
@click.option('--load-all/-no-load-all', default = False, help = 'Loads all lims sample ids')
@click.option('--load-sample/--no-load-sample', default = False, show_default = True,
                help = 'Load from sample or not. (dry-run)')
@click.pass_context

def lims(context, sample_lims_id, load_sample, load_all):
    """Read and load lims data for a given sample id"""
    adapter = context.obj['adapter']
    if load_all:
        load_all_samples(adapter)
    else:
        if load_sample:
            load_lims_sample(adapter, sample_lims_id)
        else:
            click.echo(f"Dry run...bla bla {adapter.db_name}")
            dry_run(adapter, sample_lims_id)
