import logging

from mongo_adapter import MongoAdapter
from datetime import datetime as dt
LOG = logging.getLogger(__name__)


<<<<<<< HEAD:vogue/adapter/plugin.py
class VogueAdapter(MongoAdapter):
=======


class VougeAdapter(MongoAdapter):
>>>>>>> under development!:vogue/adapter/adapter.py

    def setup(self, db_name : str):
        """Setup connection to a database"""

        if self.client is None:
            raise SyntaxError("No client is available")
        self.db = self.client[db_name]
        self.db_name = db_name
        self.sample_collection = self.db.sample
        self.analysis_collection = self.db.analysis
        
        LOG.info(f"Use database {db_name}.")

    def add_or_update_sample(self, sample_news: dict):
        """Adds/updates a sample in the database"""

        lims_id = sample_news['_id']
        update_result = self.db.sample.update_one({'_id' : lims_id}, {'$set': sample_news}, upsert=True)

        if not update_result.raw_result['updatedExisting']:
            self.db.sample.update_one({'_id' : lims_id}, 
                {'$set': {'added': dt.today()}})
            LOG.info(f"Added sample {lims_id}.")
        elif update_result.modified_count:
            self.db.sample.update_one({'_id' : lims_id}, 
                {'$set': {'updated': dt.today()}})
            LOG.info(f"Updated sample {lims_id}.")
        else:
            LOG.info(f"No updates for sample {lims_id}.")

    def sample(self, lims_id):
        return self.sample_collection.find_one({'_id':lims_id})

    def delete_sample(self):
        return None

<<<<<<< HEAD:vogue/adapter/plugin.py
    def load_analysis(self, analysis_obj):
        """Insert an analysis into the database"""
        res = self.analysis_collection.insert_one(analysis_obj)
        
        return res.inserted_id

    def analysis(self, analysis_id: str):
        """Functionality to get analyses results"""
        return self.analysis_collection.find_one({'_id':analysis_id})
        
    def find_samples(self, query:dict)-> list:
        samples = self.sample_collection.find(query)
        return list(samples)
=======
    def find_samples(self, query:dict)-> list:
        samples = self.sample_collection.find(query)
        return list(samples)

        







>>>>>>> under development!:vogue/adapter/adapter.py
