#!/usr/bin/env python
import logging
import json


LOG = logging.getLogger(__name__)

def load_sample(adapter, genotype_sample_string):

    LOG.info('Trying to build json')
    try:
        mongo_sample = json.loads(genotype_sample_string)
    except ValueError as e:
        LOG.error(e)
        return
        
    if '_id' not in mongo_sample:
        LOG.error('Not a propper mongo document. Missing _id')
        return 
        
    adapter.add_or_update_maf_analysis(mongo_sample)
