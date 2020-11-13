def build_reagent_label_category(lims_reagent_label) -> dict:
    """Build reagent label ctegory document from lims data."""

    mongo_reagent_label = {
        '_id': lims_reagent_label.name,
        'sequence': lims_reagent_label.sequence,
        'category': lims_reagent_label.category,
        'name': lims_reagent_label.name
    }

    return mongo_reagent_label
