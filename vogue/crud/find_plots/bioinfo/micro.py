#!/usr/bin/env python

import numpy as np
from vogue.constants.constants import MONTHS


def microsalt_get_strain_st(adapter, year: int) -> dict:
    """Build aggregation pipeline to get information for microsalt sequence type vs strain data."""

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
        {"$match": {"sample_info.received_date": {"$exists": "True"}}},
        {
            "$project": {
                "strain": "$sample_info.strain",
                "year": {"$year": "$sample_info.received_date"},
                "sequence_type": "$microsalt.blast_pubmlst.sequence_type",
            }
        },
        {"$match": {"year": {"$eq": int(year)}}},
        {
            "$group": {
                "_id": {"strain": "$strain", "sequence_type": "$sequence_type"},
                "number": {"$sum": 1},
            }
        },
        {
            "$match": {
                "number": {"$exists": "True"},
                "_id.sequence_type": {"$exists": "True", "$ne": ""},
            }
        },
        {
            "$group": {
                "_id": "$_id.strain",
                "number": {"$push": "$number"},
                "sequence_type": {"$push": "$_id.sequence_type"},
            }
        },
    ]

    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    plot_data = {}
    for strain_results in aggregate_result:
        strain = strain_results["_id"]
        st = strain_results["sequence_type"]
        counts = strain_results["number"]
        data = [(st[i], c) for i, c in enumerate(counts)]
        plot_data[strain] = sorted(data)
    return plot_data


def microsalt_get_qc_time(adapter, year: int, metric_path: str, category: str) -> dict:
    """Build aggregation pipeline to get information for microsalt qc data over time."""

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
                "sample_info.category": {"$eq": category},
                "sample_info.received_date": {"$exists": "True"},
            }
        },
        {
            "$project": {
                "month": {"$month": "$sample_info.received_date"},
                "year": {"$year": "$sample_info.received_date"},
                metric: "$microsalt." + metric_path,
            }
        },
        {"$match": {"year": {"$eq": int(year)}, metric: {"$not": {"$type": 2}}}},
        {
            "$group": {
                "_id": {"month": "$month"},
                metric: {"$push": f"${metric}"},
                "samples": {"$push": {metric: f"${metric}", "id": "$_id"}},
            }
        },
    ]

    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    intermediate = {
        result["_id"]["month"]: {metric: result[metric], "samples": result["samples"]}
        for result in aggregate_result
    }
    box_plots = []
    labels = []
    means = []
    outliers = []
    for m in MONTHS:
        data = intermediate.get(m[0], [])
        if data:
            values = data[metric]
            samples = data["samples"]
            box_points = calculate_box_points(values)
            outliers_this_month = get_outliers(
                month=m[0] - 1,
                metric=metric,
                samples=samples,
                minimum=box_points[0],
                maximum=box_points[-1],
            )
            outliers.extend(outliers_this_month)
            means.append(np.mean(values))
            box_plots.append(box_points)
        else:
            box_plots.append([])
        labels.append(m[1])
    plot_data = {
        "outliers": outliers,
        "data": box_plots,
        "labels": labels,
        "mean": round(np.mean(means), 2),
    }
    return plot_data


def get_outliers(month: int, metric: str, samples: list, minimum: float, maximum: float) -> list:
    """building scatter plot data for outlier samples a specific month. <metric> is what will be shown on the y axis"""

    outliers = []
    for sample in samples:
        if minimum > sample[metric] or sample[metric] > maximum:
            sample_data = {"x": month, "y": sample[metric], "name": sample["id"]}
            outliers.append(sample_data)
    return outliers


def calculate_box_points(values: list) -> list:
    """calculate box points and outliers from a list of values"""

    first_quartile = round(np.percentile(values, 25), 2)
    second_quartile = round(np.percentile(values, 50), 2)
    third_quartile = round(np.percentile(values, 75), 2)
    inter_quartile_range = third_quartile - first_quartile
    maximum = third_quartile + inter_quartile_range * 1.5
    minimum = first_quartile - inter_quartile_range * 1.5
    return [minimum, first_quartile, second_quartile, third_quartile, maximum]


def microsalt_get_untyped(adapter, year: int) -> dict:
    """Build aggregation pipeline to get information for microsalt qc data over time."""
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
        {"$match": {"sample_info.received_date": {"$exists": "True"}}},
        {
            "$project": {
                "month": {"$month": "$sample_info.received_date"},
                "year": {"$year": "$sample_info.received_date"},
                "ST": "$microsalt.blast_pubmlst.sequence_type",
            }
        },
        {"$match": {"year": {"$eq": int(year)}}},
        {"$group": {"_id": {"month": "$month"}, "ST": {"$push": "$ST"}}},
    ]

    intermediate = {}
    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    for result in aggregate_result:
        untyped = 0
        typed = 0
        untyped_lower_threshold = -9
        untyped_upper_threshold = -1
        for sequence_type in result["ST"]:
            try:
                sequence_type = int(sequence_type)
                if untyped_lower_threshold < sequence_type < untyped_upper_threshold:
                    untyped += 1
                else:
                    typed += 1
            except:
                pass
        if typed + untyped:
            fraction = untyped / (typed + untyped)
        else:
            fraction = None
        intermediate[result["_id"]["month"]] = fraction

    data = []
    labels = []
    for m in MONTHS:
        value = intermediate.get(m[0], None)
        data.append(value)
        labels.append(m[1])

    plot_data = {"data": data, "labels": labels}
    return plot_data


def microsalt_get_st_time(adapter, year: int) -> dict:
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
        {"$match": {"sample_info.received_date": {"$exists": "True"}}},
        {
            "$project": {
                "month": {"$month": "$sample_info.received_date"},
                "strain": "$sample_info.strain",
                "year": {"$year": "$sample_info.received_date"},
                "sequence_type": "$microsalt.blast_pubmlst.sequence_type",
            }
        },
        {
            "$match": {
                "year": {"$eq": int(year)},
                "sequence_type": {"$exists": "True"},
                "strain": {"$exists": "True"},
            }
        },
        {
            "$group": {
                "_id": {"month": "$month", "strain": "$strain", "sequence_type": "$sequence_type"},
                "number": {"$sum": 1},
            }
        },
    ]
    final_results = {}
    aggregate_result = list(adapter.bioinfo_samples_aggregate(pipe))
    for result in aggregate_result:
        st = result["_id"]["sequence_type"]
        strain = result["_id"]["strain"]
        if final_results.get(strain):
            final_results[strain][st] = [None] * 12
        else:
            final_results[strain] = {st: [None] * 12}
    for result in aggregate_result:
        count = result.get("number")
        if count:
            month = result["_id"]["month"]
            st = result["_id"]["sequence_type"]
            strain = result["_id"]["strain"]
            final_results[strain][st][month - 1] = count

    return {"data": final_results, "labels": [m[1] for m in MONTHS]}
