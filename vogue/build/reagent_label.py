from genologics.entities import Process

from vogue.parse.build.reagent_label import reagent_label_data


def build_reagent_label(step: Process) -> dict:
    """Build reagent label document from lims data."""
    reagent_labels = reagent_label_data(step)

    return reagent_labels
