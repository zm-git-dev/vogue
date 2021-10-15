from typing import Optional


from vogue.adapter import VogueAdapter
from vogue.models.database.sample import Sample
from vogue.models.database.bioinfo_sample.base import BioInfoSample


def find_sample(adapter: VogueAdapter, sample_id: str) -> Optional[Sample]:
    """Find one sample from the sample collection"""

    db_sample = adapter.sample_collection.find_one({"_id": sample_id})
    if not db_sample:
        return None

    return Sample(**db_sample)


def find_bioinfo_sample(adapter: VogueAdapter, sample_id: str) -> Optional[BioInfoSample]:
    """Find one sample from the sample collection"""

    db_sample = adapter.bioinfo_samples_collection.find_one({"_id": sample_id})
    if not db_sample:
        return None

    return BioInfoSample(**db_sample)
