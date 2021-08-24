from vogue.build.reagent_label_category import build_reagent_label_category
import logging

LOG = logging.getLogger(__name__)


def load_all(adapter, lims, categories):
    """Function to load reagent_labels from a step into the database"""

    LOG.info("Fetching all reagent types from lims...")
    lims_reagent_labels = lims.get_reagent_types()
    LOG.info("Loading reagent types into the reagent_label_cathegory colleciton.")
    for lims_reagent_label in lims_reagent_labels:
        if lims_reagent_label.category not in categories:
            continue
        mongo_reagent_label = build_reagent_label_category(lims_reagent_label)
        adapter.add_or_update_document(
            mongo_reagent_label, adapter.reagent_label_category_collection
        )
