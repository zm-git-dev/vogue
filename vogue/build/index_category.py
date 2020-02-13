def build_index_category(lims_index)-> dict:
    """Build flowcell document from lims data."""

    mongo_index = {'_id': lims_index.name,
                   'sequence': lims_index.sequence,
                   'category': lims_index.category,
                   'name': lims_index.name}

    return mongo_index
