from pydantic import BaseModel


class MultiqcPicardAlignmentSummaryMetrics(BaseModel):
    total_reads: int  # ?
    pct_pf_reads_aligned: float
    mean_read_length: float


class MultiqcPicardInsertSize(BaseModel):
    medin_insert_size: int


class MultiqcPicardWGSMetrics(BaseModel):
    median_coverage: float
    pct_10x: float
    pct_30x: float
    pct_50x: float
    pct_100x: float


class MultiqcCutadapt(BaseModel):
    percent_trimmed: float


class MultiqcGeneralStats(BaseModel):
    Fastqc_mqc_generalstats_fastqc_percent_duplicates: float
    Fastqc_mqc_generalstats_fastqc_percent_gc: float
    Fastqc_mqc_generalstats_fastqc_total_sequences: float


class Mutant(BaseModel):
    multiqc_picard_alignment_summary_metrics: MultiqcPicardAlignmentSummaryMetrics
    multiqc_picard_insertSize: MultiqcPicardInsertSize
    multiqc_picard_wgsmetrics: MultiqcPicardWGSMetrics
    multiqc_cutadapt: MultiqcCutadapt
    multiqc_general_stats: MultiqcGeneralStats
