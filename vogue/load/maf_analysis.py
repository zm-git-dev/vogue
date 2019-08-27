from vogue.build.maf_analysis import build_sample
from vogue.external_models.genotype_models import *

import logging
import datetime

LOG = logging.getLogger(__name__)


def load_one(adapter, sample_id):
    sample = Sample.query.filter(Sample.id == sample_id).first()
    mongo_sample = build_sample(sample)
    adapter.add_or_update_maf_analysis(mongo_sample)

def load_all(adapter):
    samples = Sample.query.all()
    for sample in samples:
        mongo_sample = build_sample(sample)
        adapter.add_or_update_maf_analysis(mongo_sample)

def load_many(adapter, days=120):
    current_time = datetime.datetime.utcnow()
    some_days_ago = current_time - datetime.timedelta(days = days)
    samples = Sample.query.filter(Sample.created_at > some_days_ago).all()
    for sample in samples:
        mongo_sample = build_sample(sample)
        adapter.add_or_update_maf_analysis(mongo_sample)

