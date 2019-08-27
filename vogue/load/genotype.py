import logging

LOG = logging.getLogger(__name__)

def load_sample(adapter, mongo_sample):
    adapter.add_or_update_maf_analysis(mongo_sample)