import logging
from vogue.build.sample import build_sample
LOG = logging.getLogger(__name__)
from vogue.constants.constants import TEST_SAMPLES


def load_one(adapter, lims, lims_sample=None, date=None):
    """Function to load one lims sample into the database"""

    if not lims_sample.udf.get('Delivered'):
        LOG.info('Will not add to database. Sample not delivered.')
        return

    if date and (lims_sample.udf.get('Delivered') < date):
        LOG.info('Sample odler than the set date.')
        return

    if lims_sample.id in TEST_SAMPLES:
        return

    mongo_sample = build_sample(lims_sample, lims, adapter)
    adapter.add_or_update_sample(mongo_sample)


def load_all(adapter, lims, start_sample = None, new_only=True, date = None):
    """Function to load all lims samples into the database"""
    delivered_samples = lims.get_samples(udf={'Sample Delivered' : True})
    samples_in_database = list(adapter.sample_collection_ids())[0]['ids']
    for sample in delivered_samples:
        if sample.id in samples_in_database:
            continue
        if not start_sample:
            load_one(adapter, lims, lims_sample=sample, date=date)
        elif start_sample and start_sample == sample.id:
            start_sample = None


def load_one_dry(lims_sample, lims, adapter):
    existing_sample = adapter.sample(lims_sample.id)
    if existing_sample:
        LOG.info("The sample exists in the database.")
    else:
        LOG.info("The sample does not exists in the database.")
    mongo_sample = build_sample(lims_sample, lims, adapter)
    LOG.info("Sample informamtion from lims to add/update: \n %s", mongo_sample)
    return


def load_all_dry():
    LOG.info('Will load all lims samples.')
    return
 


        