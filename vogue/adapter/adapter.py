from mongo_adapter import MongoAdapter
from datetime import datetime as dt
import logging
LOG = logging.getLogger(__name__)


class VougeAdapter(MongoAdapter):

    def setup(self, db_name : str):
        """Setup connection to a database"""

        if self.client is None:
            raise SyntaxError("No client is available")

        self.db = self.client[db_name]
        self.sample_collection = self.db.sample
        LOG.info(f"Use database {db_name}.")


    def add_or_update_sample(self, sample_news: dict):
        """Adds/updates a sample in the database"""

        lims_id = sample_news['_id']
        update_result = self.db.sample.update_one({'_id' : lims_id}, {'$set': sample_news}, upsert=True)

        if not update_result.raw_result['updatedExisting']:
            self.db.sample.update_one({'_id' : lims_id}, 
                {'$set': {'added': dt.today().date().isoformat()}}, upsert=True)
            LOG.info(f"Added sample {lims_id}.")
        elif update_result.modified_count:
            self.db.sample.update_one({'_id' : lims_id}, 
                {'$set': {'updated': dt.today().date().isoformat()}}, upsert=True)
            LOG.info(f"Updated sample {lims_id}.")                
        else:
            LOG.info(f"No updates for sample {lims_id}.")


    def delte_sample(self):
        return None

