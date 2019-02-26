import logging

from mongo_adapter import MongoAdapter
from datetime import datetime as dt
LOG = logging.getLogger(__name__)


class VougeAdapter(MongoAdapter):

    def setup(self, db_name : str):
        """Setup connection to a database"""

        if self.client is None:
            raise SyntaxError("No client is available")
        self.db = self.client[db_name]
        self.db_name = db_name
        self.sample_collection = self.db.sample
        self.analysis_collection = self.db.analysis
        self.app_tag_collection = self.db.application_tag
        
        LOG.info("Use database %s.", db_name)

    def add_or_update_sample(self, sample_news: dict):
        """Adds/updates a sample in the database"""

        lims_id = sample_news['_id']
        update_result = self.db.sample.update_one({'_id' : lims_id}, {'$set': sample_news}, upsert=True)

        if not update_result.raw_result['updatedExisting']:
            self.db.sample.update_one({'_id' : lims_id}, 
                {'$set': {'added': dt.today()}})
            LOG.info("Added sample %s.", lims_id)
        elif update_result.modified_count:
            self.db.sample.update_one({'_id' : lims_id}, 
                {'$set': {'updated': dt.today()}})
            LOG.info("Updated sample %s.", lims_id)
        else:
            LOG.info("No updates for sample %s.", lims_id)

    def add_or_update_application_tag(self, application_tag_news: dict):
        """Adds/updates a application_tag in the database"""

        tag = application_tag_news['_id']
        update_result = self.db.application_tag.update_one({'_id' : tag}, 
                            {'$set': application_tag_news}, upsert=True)

        if not update_result.raw_result['updatedExisting']:
            self.db.application_tag.update_one({'_id' : tag}, 
                {'$set': {'added': dt.today()}})
            LOG.info("Added application_tag %s.", tag)
        elif update_result.modified_count:
            self.db.application_tag.update_one({'_id' : tag}, 
                {'$set': {'updated': dt.today()}})
            LOG.info("Updated application_tag %s.", tag)
        else:
            LOG.info("No updates for application_tag %s.", tag)

    def sample(self, lims_id):
        return self.sample_collection.find_one({'_id':lims_id})

    def app_tag(self, tag):
        return self.app_tag_collection.find_one({'_id':tag})

    def delete_sample(self):
        return None

    def add_or_update_analysis(self, analysis_result: dict):
        """Functionality to add or update analysis sample"""
        lims_id = analysis_result['_id']
        update_result = self.db.analysis.update_one({'_id' : lims_id}, {'$set': analysis_result}, upsert=True)

        if not update_result.raw_result['updatedExisting']:
            self.db.analysis.update_one({'_id' : lims_id}, 
                {'$set': {'added': dt.today()}})
            LOG.info("Added analysis sample %s.", lims_id)
        elif update_result.modified_count:
            self.db.analysis.update_one({'_id' : lims_id}, 
                {'$set': {'updated': dt.today()}})
            LOG.info("Updated analysis for sample %s.", lims_id)
        else:
            LOG.info("No analysis updates for sample %s.", lims_id)

    def analysis(self, analysis_id: str):
        """Functionality to get analyses results"""
        return self.analysis_collection.find_one({'_id':analysis_id})
        
    def find_samples(self, query:dict)-> list:
        samples = self.sample_collection.find(query)
        return list(samples)
