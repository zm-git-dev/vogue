from vogue.load.lims import build_sample

from genologics.lims import Lims
from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
lims = Lims(BASEURI,USERNAME,PASSWORD)

def dry_run(adapter, lims_id):
    lims_sample = Sample(lims, id = lims_id)
    new_sample = build_sample(lims_sample)
    existing_sample = adapter.sample_collection.find_one({'_id':lims_id})
    if existing_sample:
        print(f"The sample exist in the database and will be updated.")
    else:
        print(f"The sample does not exist in the database.")
    print(f"Sample informamtion from lims to add/update: \n {new_sample}")
    

def build_and_update(adapter, lims_sample):
    mongo_sample = build_sample(lims_sample)
    adapter.add_or_update_sample(mongo_sample)

def load_one_sample(adapter, lims_id):
    lims_sample = Sample(lims, id = lims_id)
    build_and_update(adapter, lims_sample)

def load_all_samples(adapter):
    for sample in lims.get_samples():
        print(sample.id)
        build_and_update(adapter, sample)