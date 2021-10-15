#!/usr/bin/env python

from vogue.constants.constants import MONTHS, DNA_PICARD

VALID_WORKFLOWS = ["balsamic", "mip-dna"]
VALID_APPLICATION = ["wgs", "tga", "wes"]


def qc_dna_picard_time_plot(adapter, year: int) -> dict:
    """Prepares data for the picard over time plot."""

    pipe = [
        {
            "$lookup": {
                "from": "sample",
                "localField": "_id",
                "foreignField": "_id",
                "as": "sample_info",
            }
        },
        {"$unwind": {"path": "$sample_info"}},
        {"$match": {"sample_info.received_date": {"$exists": "True"}}},
        {
            "$project": {
                "mip-dna": 1,
                "balsamic": 1,
                "workflows": 1,
                "received_date": "$sample_info.received_date",
                "category": "$sample_info.category",
            }
        },
        {"$match": {"received_date": {"$exists": "True"}}},
        {
            "$project": {
                "month": {"$month": "$received_date"},
                "year": {"$year": "$received_date"},
                "mip-dna": 1,
                "balsamic": 1,
                "workflows": 1,
                "category": 1,
            }
        },
        {"$match": {"year": {"$eq": int(year)}}},
    ]
    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    final_data = {}
    for data in DNA_PICARD.values():
        for key in data:
            final_data[key] = {}

    for sample in aggregate_result:
        qc_dna_analysis = sample.get("balsamic")
        if not qc_dna_analysis:
            qc_dna_analysis = sample.get("mip-dna")
            if not qc_dna_analysis:
                continue
        qc_data_to_process = qc_dna_analysis.get("multiqc_picard_insertSize")
        if qc_data_to_process:
            final_data = _append_to_final_data(
                final_data=final_data, raw_data=qc_data_to_process, sample=sample
            )

        qc_data_to_process = qc_dna_analysis.get("multiqc_picard_HsMetrics")
        if qc_data_to_process:
            final_data = _append_to_final_data(
                final_data=final_data, raw_data=qc_data_to_process, sample=sample
            )

    plot_data = {"data": final_data, "labels": [m[1] for m in MONTHS]}
    return plot_data


def _append_to_final_data(final_data: dict, raw_data: dict, sample: dict):
    """Parsing raw data. Appending to final_data"""

    for key, val in raw_data.items():
        if key in final_data.keys():
            category = f"{sample['category']}_{'_'.join(sample['workflows'])}"
            if category not in final_data[key].keys():
                final_data[key][category] = []
            final_data[key][category].append(
                {
                    "name": sample["_id"],
                    "application": sample["category"],
                    "workflows": ",".join(sample["workflows"]),
                    "x": sample["month"],
                    "y": val,
                }
            )
    return final_data


def qc_dna_picard_plot(adapter, year: int) -> dict:
    """Prepares data for the picard plot."""

    all_samples = adapter.bioinfo_samples_collection.find()
    final_data = []

    for sample in all_samples:
        sample_id = sample["_id"]
        qc_dna_analysis = sample.get("balsamic")
        if not qc_dna_analysis:
            qc_dna_analysis = sample.get("mip-dna")
            if not qc_dna_analysis:
                continue
        multiqc_picard_insertSize = qc_dna_analysis.get("multiqc_picard_insertSize")
        multiqc_picard_HsMetrics = qc_dna_analysis.get("multiqc_picard_HsMetrics")
        merged = multiqc_picard_insertSize.copy()
        merged.update(multiqc_picard_HsMetrics)
        merged["_id"] = sample_id
        final_data.append(merged)

    plot_data = {"final_data": final_data, "labels": [m[1] for m in MONTHS]}

    return plot_data
