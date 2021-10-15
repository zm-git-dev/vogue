import logging

from mongo_adapter import MongoAdapter
from pymongo.collection import Collection

from datetime import datetime as dt

LOG = logging.getLogger(__name__)


def check_dates(analysis_result, current_document):
    """Function to pop analysysis results from tne new analysis if the results are older than
    the current results in the database"""

    if current_document and current_document.get("mip_dna") and analysis_result.get("mip_dna"):
        try:
            if current_document["mip_dna"]["added"] > analysis_result["mip_dna"]["added"]:
                analysis_result.pop("mip_dna")
        except:
            LOG.error("Invalid or missing mip_dna analysis date. Skiping analysis")
            analysis_result.pop("mip_dna")

    return analysis_result


class VogueAdapter(MongoAdapter):
    def setup(self, db_name: str):
        """Setup connection to a database"""

        if self.client is None:
            raise SyntaxError("No client is available")
        self.db = self.client[db_name]
        self.db_name = db_name
        self.sample_collection: Collection = self.db.sample
        self.bioinfo_processed_collection = self.db.bioinfo_processed
        self.bioinfo_raw_collection = self.db.bioinfo_raw
        self.bioinfo_samples_collection = self.db.bioinfo_samples
        self.app_tag_collection = self.db.application_tag
        self.flowcell_collection = self.db.flowcell
        self.reagent_label_collection = self.db.reagent_label
        self.reagent_label_category_collection = self.db.reagent_label_category
        self.genotype_analysis_collection = self.db.genotype_analysis

        LOG.info("Use database %s.", db_name)

    def add_or_update_document(self, document_news: dict, collection):
        """Adds/updates a document in the database"""

        document_id = document_news["_id"]

        update_result = collection.update_one(
            {"_id": document_id}, {"$set": document_news}, upsert=True
        )

        if not update_result.raw_result["updatedExisting"]:
            collection.update_one({"_id": document_id}, {"$set": {"added": dt.today()}})
            LOG.info("Added document %s.", document_id)
        elif update_result.modified_count:
            collection.update_one({"_id": document_id}, {"$set": {"updated": dt.today()}})
            LOG.info("Updated document %s.", document_id)
        else:
            LOG.info("No updates for document %s.", document_id)

    def add_or_update_bioinfo_raw(self, analysis_result: dict):
        """Functionality to add or update analysis for unprocessed aka raw bioinfo stat"""
        case_id = analysis_result["_id"]
        # pop _id key to make pushing easier
        analysis_result.pop("_id")
        update_result = self.db.bioinfo_raw.find_one({"_id": case_id})

        if update_result is None:
            self.db.bioinfo_raw.update_one(
                {"_id": case_id},
                {"$set": {**analysis_result, **{"added": dt.today()}}},
                upsert=True,
            )
            LOG.info("Added analysis sample %s.", case_id)
        else:
            self.db.bioinfo_raw.update_one(
                {"_id": case_id},
                {"$set": {**analysis_result, **{"updated": dt.today()}}},
                upsert=True,
            )
            LOG.info("Updated analysis for sample %s.", case_id)

    def add_or_update_bioinfo_processed(self, analysis_result: dict):
        """Functionality to add or update analysis for processed bioinfo stat"""
        case_id = analysis_result["_id"]
        # pop _id key to make pushing easier
        analysis_result.pop("_id")
        update_result = self.db.bioinfo_processed.find_one({"_id": case_id})

        if update_result is None:
            self.db.bioinfo_processed.update_one(
                {"_id": case_id},
                {"$set": {**analysis_result, **{"added": dt.today()}}},
                upsert=True,
            )
            LOG.info("Added analysis sample %s.", case_id)
        else:
            self.db.bioinfo_processed.update_one(
                {"_id": case_id},
                {"$set": {**analysis_result, **{"updated": dt.today()}}},
                upsert=True,
            )
            LOG.info("Updated analysis for sample %s.", case_id)

    def add_or_update_bioinfo_samples(self, analysis_result: dict):
        """Functionality to add or update bioinfo analysis for sample level results"""
        lims_id = analysis_result["_id"]
        current_document = self.db.bioinfo_samples.find_one({"_id": lims_id})
        analysis_result = check_dates(analysis_result, current_document)

        update_result = self.db.bioinfo_samples.update_one(
            {"_id": lims_id}, {"$set": analysis_result}, upsert=True
        )

        if not update_result.raw_result["updatedExisting"]:
            self.db.bioinfo_samples.update_one({"_id": lims_id}, {"$set": {"added": dt.today()}})
            LOG.info("Added sample %s.", lims_id)
        elif update_result.modified_count:
            self.db.bioinfo_samples.update_one({"_id": lims_id}, {"$set": {"updated": dt.today()}})
            LOG.info("Updated sample %s.", lims_id)
        else:
            LOG.info("No updates for sample %s.", lims_id)

    def sample(self, lims_id):
        return self.sample_collection.find_one({"_id": lims_id})

    def flowcell(self, run_id):
        return self.flowcell_collection.find_one({"_id": run_id})

    def app_tag(self, tag):
        return self.app_tag_collection.find_one({"_id": tag})

    def delete_sample(self):
        return None

    def sample_analysis(self, analysis_id: str):
        """Functionality to get analyses results"""
        return self.bioinfo_samples_collection.find_one({"_id": analysis_id})

    def bioinfo_raw(self, analysis_id: str):
        """Functionality to get analyses results"""
        return self.bioinfo_raw_collection.find_one({"_id": analysis_id})

    def bioinfo_processed(self, analysis_id: str):
        """Functionality to get analyses results"""
        return self.bioinfo_processed_collection.find_one({"_id": analysis_id})

    def find_samples(self, query: dict) -> list:
        """Function to find samples in samples collection based on query"""
        samples = self.sample_collection.find(query)
        return list(samples)

    def samples_aggregate(self, pipe: list):
        """Function to make a aggregation on the sample colleciton"""
        return self.sample_collection.aggregate(pipe)

    def flowcells_aggregate(self, pipe: list):
        """Function to make a aggregation on the flowcell colleciton"""
        return self.flowcell_collection.aggregate(pipe)

    def bioinfo_samples_aggregate(self, pipe: list):
        """Function to make a aggregation on the sample analysis colleciton"""
        return self.bioinfo_samples_collection.aggregate(pipe)

    def sample_collection_ids(self):
        pipe = [{"$project": {"_id": 1}}, {"$group": {"_id": None, "ids": {"$addToSet": "$_id"}}}]
        return self.sample_collection.aggregate(pipe)

    def genotype_analysis_aggregate(self, pipe: list):
        """Function to make a aggregation on the genotype analysis colleciton"""
        return self.genotype_analysis_collection.aggregate(pipe)

    def find_genotype_plate(self, plate_id: str):
        """find all samples from plate"""
        return self.genotype_analysis_collection.find({"plate": plate_id})

    def get_category(self, app_tag):
        """Function get category based on application tag from the application tag collection"""
        tag = self.app_tag_collection.find_one({"_id": app_tag}, {"category": 1})
        return tag.get("category") if tag else None

    def get_reagent_label_category(self, reagent_label):
        """Function get category based on application tag from the application tag collection"""
        category = self.app_tag_collection.find_one({"name": reagent_label}, {"category": 1})
        return category.get("category") if category else None

    def reagent_label_aggregate(self, pipe: list):
        """Function to make a aggregation on the reagent_label analysis colleciton"""
        return self.reagent_label_collection.aggregate(pipe)

    def get_all_reagent_label_names_grouped_by_category(self):
        """Function get all reagent label names grouped by category
        from the reagent_label_category colleciton"""
        pipe = [
            {"$group": {"_id": {"category": "$category"}, "reagent_labels": {"$push": "$name"}}}
        ]
        return self.reagent_label_category_collection.aggregate(pipe)

    def get_reagent_label_categories(self):
        """Function to get all categories from label_category_collection"""
        pipe = [
            {"$project": {"category": 1}},
            {"$group": {"_id": None, "categories": {"$addToSet": "$category"}}},
        ]
        reagent_label_categories = self.reagent_label_category_collection.aggregate(pipe)
        return list(reagent_label_categories)[0]["categories"]
