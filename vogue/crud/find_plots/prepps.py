#!/usr/bin/env python

import numpy as np


def find_concentration_amount(adapter, year: int = None) -> dict:
    """Prepares data for a scatter plot showning Concentration agains Amount."""

    amount = {"data": []}
    pipe = [
        {
            "$match": {
                "received_to_delivered": {"$exists": True},
                "amount": {"$exists": True},
                "amount-concentration": {"$exists": True},
            }
        },
        {"$project": {"year": {"$year": "$received_date"}, "amount": 1, "amount-concentration": 1}},
        {"$match": {"year": {"$eq": int(year)}}},
    ]

    aggregate_result = adapter.samples_aggregate(pipe)
    for sample in aggregate_result:
        if sample["amount"] > 200:
            sample["amount"] = 200
        amount["data"].append(
            {
                "x": sample["amount"],
                "y": round(sample["amount-concentration"], 2),
                "name": sample["_id"],
            }
        )
    return amount


def find_concentration_defrosts(adapter, year: int) -> dict:
    """Prepares data for a plot showning Number of defrosts against Concentration"""

    nr_defrosts = list(adapter.sample_collection.distinct("nr_defrosts"))
    defrosts = {
        "axis": {"x": "Number of Defrosts", "y": "Concentration (nM)"},
        "data": {},
        "title": "wgs illumina PCR-free",
        "labels": nr_defrosts.sort(),
    }

    pipe = [
        {
            "$match": {
                "received_to_delivered": {"$exists": True},
                "nr_defrosts-concentration": {"$exists": True},
                "nr_defrosts": {"$exists": True},
                "lotnr": {"$exists": True},
            }
        },
        {
            "$project": {
                "year": {"$year": "$received_date"},
                "nr_defrosts-concentration": 1,
                "nr_defrosts": 1,
                "lotnr": 1,
            }
        },
        {"$match": {"year": {"$eq": int(year)}}},
        {
            "$group": {
                "_id": {"nr_defrosts": "$nr_defrosts", "lotnr": "$lotnr"},
                "count": {"$sum": 1},
                "values": {"$push": "$nr_defrosts-concentration"},
            }
        },
        {"$sort": {"_id.nr_defrosts": 1}},
    ]
    aggregate_result = adapter.samples_aggregate(pipe)

    for result in aggregate_result:
        group = result["_id"]["lotnr"]
        if group not in defrosts["data"]:
            defrosts["data"][group] = {"median": [], "quartile": [], "nr_samples": []}
        nr = result["_id"]["nr_defrosts"]
        values = np.array(result["values"])
        defrosts["data"][group]["median"].append([nr, round(np.percentile(values, 50), 2)])
        defrosts["data"][group]["quartile"].append(
            [nr, round(np.percentile(values, 25), 2), round(np.percentile(values, 75), 2)]
        )
        defrosts["data"][group]["nr_samples"].append([nr, result["count"]])

    return defrosts
