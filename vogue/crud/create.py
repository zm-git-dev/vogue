from vogue.adapter import VogueAdapter
from vogue.models.database import Sample, BioInfoSample
from vogue.crud.find import find_sample, find_bioinfo_sample
from vogue.exceptions import InsertError
from pymongo.results import InsertOneResult

import logging

LOG = logging.getLogger(__name__)


def create_sample(adapter: VogueAdapter, sample: Sample) -> str:
    """Function to load a new sample to the database."""

    if find_sample(adapter=adapter, sample_id=sample.id):
        raise InsertError(f"Sample {sample.id} already exist in sample collection.")

    result: InsertOneResult = adapter.sample_collection.insert_one(sample.dict(by_alias=True))
    LOG.info("Added sample document %s.", sample.id)

    return result.inserted_id


def create_bioinfo_sample(adapter: VogueAdapter, sample: BioInfoSample) -> str:
    """Function to load a new sample to the database."""

    if find_bioinfo_sample(adapter=adapter, sample_id=sample.id):
        raise InsertError(
            f"Bioinfo Sample {sample.id} already exist in bioinfo_samples collection."
        )

    result: InsertOneResult = adapter.bioinfo_samples_collection.insert_one(
        sample.dict(by_alias=True)
    )
    LOG.info("Added bioinfo sample document %s.", sample.id)

    return result.inserted_id
