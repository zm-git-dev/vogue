#!/usr/bin/env python
import logging
import json
from dateutil.parser import parse

LOG = logging.getLogger(__name__)


def load_sample(adapter, genotype_sample_string):

    LOG.info("Trying to build json")
    try:
        mongo_sample = json.loads(genotype_sample_string)
        if mongo_sample.get("sample_created_in_genotype_db"):
            date = parse(mongo_sample["sample_created_in_genotype_db"])
            mongo_sample["sample_created_in_genotype_db"] = date
    except ValueError as e:
        LOG.error(e)
        return

    if "_id" not in mongo_sample:
        LOG.error("Not a propper mongo document. Missing _id")
        return

    adapter.add_or_update_document(mongo_sample, adapter.genotype_analysis_collection)
