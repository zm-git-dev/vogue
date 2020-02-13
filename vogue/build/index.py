from genologics.entities import Process

from vogue.parse.build.index import index_data

def build_index(step: Process)-> dict:
    """Build flowcell document from lims data."""
    indexes = index_data(step)

    return indexes
