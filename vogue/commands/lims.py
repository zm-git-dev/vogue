import pymongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.trending
from vogue.load.lims import MongoSample
from argparse import ArgumentParser

from mongo_adapter import (MongoAdapter, get_client)

from genologics.lims import Lims
from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
lims = Lims(BASEURI,USERNAME,PASSWORD)

DESC = ''

class VougeAdapter(MongoAdapter):
    def __init__(self,lims_sample_id):
        self.sample_collection = self.db.sample
    
    
    def add_sample(mongo_sample):
        """Adds a sample to the database
        
        Args:
            sample(dict)

        Returns:
            inserted_id(str)
        """
        # Code to add a sample
        new_id = self.sample_collection.insert_one(mongo_sample).inserted_id


def build_sample(sample):
    MS = MongoSample(sample)

    new_id = db.sample.insert_one(MS.mongo_sample).inserted_id

def build_all():
    for sample in lims.get_samples():
        build_sample(sample)

def main(args):
    if args.sample_id:
        sample = Sample(lims, id = args.sample_id)
        build_sample(sample)
    else:
        build_all()        


if __name__ == "__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('-s', dest = 'sample_id', default = None,
                        help='Sample Lims id for')
                 

    args = parser.parse_args()

    main(args)