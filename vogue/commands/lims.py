import pymongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.trending
from vogue.load.lims import build_sample
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
    
    def connect(self, db_uri, debug=False):
        """Configure connection to a SQL database.
         .. versionadded:: 2.1.0
         Args:
            db_uri (str): path/URI to the database to connect to
            debug (Optional[bool]): whether to output logging information
        """
        
        # connect to the mongo database
        if db_uri == "mongodb://":
            db_uri = "mongodb://localhost:27017"
            LOG.info('Set uri to %s', db_uri)
        
        db_name = 'chanjo'
        if not 'mock' in db_uri:
            uri_info = uri_parser.parse_uri(db_uri)
            db_name = uri_info['database'] or db_name
            
        self.uri = db_uri
        self.client = get_client(uri=db_uri)
        
        self.setup(db_name=db_name)


    def setup(self, db_name='chanjo'):
        """Overrides the basic setup method"""
        if self.client == None:
            raise SyntaxError("No client available")
        
        if self.db is None:
            self.db = self.client[db_name]
        self.db_name = db_name
        self.session = Session(self.db)
        
        self.transcripts_collection = self.db.transcript
        self.sample_collection = self.db.sample
        self.transcript_stat_collection = self.db.transcript_stat
        
        

    
    def add_sample(mongo_sample):
        """Adds a sample to the database
        
        Args:
            sample(dict)

        Returns:
            inserted_id(str)
        """
        # Code to add a sample
        
        new_id = self.sample_collection.insert_one(mongo_sample).inserted_id









def build(sample):
    mongo_sample = build_sample(sample)
    new_id = db.sample.insert_one(mongo_sample).inserted_id

def build_all():
    for sample in lims.get_samples():
        build(sample)

def main(args):
    if args.sample_id:
        sample = Sample(lims, id = args.sample_id)
        build(sample)
    else:
        build_all()        


if __name__ == "__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('-s', dest = 'sample_id', default = None,
                        help='Sample Lims id for')
                 

    args = parser.parse_args()

    main(args)