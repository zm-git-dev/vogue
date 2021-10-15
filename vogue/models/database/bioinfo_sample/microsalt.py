from typing import Literal, List
from pydantic import BaseModel


class BlastPubmlst(BaseModel):
    sequence_type: int
    thresholds: Literal["Passed", "Failed"]


class QuastAssembly(BaseModel):
    estimated_genome_length: int
    gc_percentage: float
    n50: int
    necessary_contigs: int


class PicardMarkDuplicate(BaseModel):
    insert_size: int
    duplication_rate: float


class MicroSaltSamtoolsStats(BaseModel):
    total_reads: int
    mapped_rate: float
    average_coverage: float
    coverage_10x: float
    coverage_30x: float
    coverage_50x: float
    coverage_100x: float


class MicroSalt(BaseModel):
    blast_pubmlst: BlastPubmlst
    quast_assembly: QuastAssembly
    blast_resfinder_resistence: List[str]
    picard_markduplicate: PicardMarkDuplicate
    microsalt_samtools_stats: MicroSaltSamtoolsStats
