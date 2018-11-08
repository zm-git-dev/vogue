import logging
import click
from vogue.load.sample import load_one_sample, load_all_samples


@click.command("lims", short_help = "load lims into db.")
@click.option('-s', '--sample-lims-id', help = 'Input sample lims id')
@click.option('--load-all', is_flag = True, help = 'Loads all lims sample ids')
@click.option('--dry', is_flag = True, help = 'Load from sample or not. (dry-run)')
@click.pass_context


def lims(context, sample_lims_id, dry, load_all):
    """Read and load lims data for a given sample id"""
    adapter = context.obj['adapter']
    lims = context.obj['lims']

    if load_all:
        load_all_samples(adapter, lims=lims, dry_run=dry)
        return

    load_one_sample(adapter, sample_lims_id, lims=lims, dry_run=dry)
