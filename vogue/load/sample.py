from vogue.load.lims import build_sample

from genologics.lims import Lims
from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
lims = Lims(BASEURI,USERNAME,PASSWORD)


def load_lims_sample(adapter, lims_id):
    lims_sample = Sample(lims, id = lims_id)
    mongo_sample = build_sample(lims_sample)
    adapter.add_or_update_sample(mongo_sample)

def dry_run(adapter, lims_id):
    lims_sample = Sample(lims, id = lims_id)
    mongo_sample = build_sample(lims_sample)
    print(mongo_sample)
    
def load_all_samples(adapter):
    for sample in lims.get_samples():
        print(sample.id)
        load_lims_sample(adapter, sample.id)