#!/usr/bin/env python


def get_qc(adapter, year: int, metric_path: str) -> dict:
    """Prepares data for covid scatter plot"""

    metric = metric_path.split(".")[1]

    pipe = [
        {"$match": {"microsalt": {"$exists": "True"}}},
        {
            "$lookup": {
                "from": "sample",
                "localField": "_id",
                "foreignField": "_id",
                "as": "sample_info",
            }
        },
        {"$unwind": {"path": "$sample_info"}},
        {
            "$match": {
                "sample_info.category": {"$eq": "cov"},
                "sample_info.prepared_date": {"$exists": "True"},
                "sample_info.prep_method": {"$exists": "True"},
            }
        },
        {
            "$project": {
                "year": {"$year": "$sample_info.prepared_date"},
                "prep_method": "$sample_info.prep_method",
                "date": "$sample_info.prepared_date",
                metric: f"$microsalt.{metric_path}",
            }
        },
        {"$match": {"year": {"$eq": int(year)}}},
        {
            "$group": {
                "_id": {"prep_method": "$prep_method"},
                "data": {"$push": {metric: f"${metric}", "date": "$date", "id": "$_id"}},
            }
        },
    ]

    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    results = {}
    for group_data in aggregate_result:
        group = group_data["_id"]["prep_method"]
        results[group] = []
        for sample in group_data["data"]:
            results[group].append([sample["date"], sample[metric], sample["id"]])

    return results
