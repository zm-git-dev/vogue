from genologics.entities import Process

from vogue.parse.build.reagent_label import reagent_label_data

def build_reagent_label(lims, step: Process)-> dict:
    """Build flowcell document from lims data."""
    reagent_labels = reagent_label_data(lims, step)

    return reagent_labels
