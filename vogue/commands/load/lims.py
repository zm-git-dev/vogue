import click

from .single import single as single_command
from .multi import multi as multi_command

@click.group()
@click.pass_context

def lims(context):
    """
    Read and load lims data for a given sample id
    """
    pass

lims.add_command(single_command)
lims.add_command(multi_command)
