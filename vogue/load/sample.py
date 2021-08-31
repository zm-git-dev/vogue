import logging
from vogue.build.sample import build_sample

LOG = logging.getLogger(__name__)
from vogue.constants.constants import TEST_SAMPLES


def load_one(adapter, lims_sample=None, lims=None):
    """Function to load one lims sample into the database"""

    if lims_sample.id in TEST_SAMPLES:
        return

    mongo_sample = build_sample(lims_sample, lims, adapter)
    adapter.add_or_update_document(mongo_sample, adapter.sample_collection)


def load_all(adapter, lims, start_sample=None):
    """Function to load all lims samples into the database"""

    all_samples = lims.get_samples()
    total_nr_samples = len(all_samples)
    for nr, sample in enumerate(all_samples):
        if not start_sample:
            LOG.info("%s/%s %s" % (nr, total_nr_samples, sample.id))
            load_one(adapter, lims_sample=sample, lims=lims)
        elif start_sample and start_sample == sample.id:
            start_sample = None


def load_recent(adapter, lims, the_date):
    """Function to load all lims samples into the database"""

    latest_processes = lims.get_processes(last_modified=the_date)
    samples = []
    LOG.info("Found %s processes modified since %s.", len(latest_processes), the_date)
    LOG.info("Fetching recently updated samples...")
    for process in latest_processes:
        for analyte in process.all_inputs():
            samples += analyte.samples
    unique_samples = set(samples)
    nr_unique_samples = len(unique_samples)
    LOG.info("%s samples will be added or updated.", nr_unique_samples)
    for nr, sample in enumerate(unique_samples):
        LOG.info("%s/%s %s" % (nr, nr_unique_samples, sample.id))
        load_one(adapter, lims_sample=sample, lims=lims)


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
    LOG.info("Will load all lims samples.")
    return
