#!/usr/bin/env python

from vogue.constants.constants import LANE_UDFS


def instrument_info(adapter, year: int, metric: str) -> dict:
    """Prepares data for a plot Q30 values for diferent runs over time"""
    instruments = {"axis": {"y": "Average Q30"}, "data": {p: {} for p in LANE_UDFS}, "title": "Q30"}
    pipe = [
        {"$project": {"year": {"$year": "$date"}, "instrument": 1, "date": 1, "avg": 1}},
        {"$match": {"year": {"$eq": int(year)}}},
        {
            "$group": {
                "_id": {"instrument": "$instrument"},
                "data": {"$push": {metric: "$avg." + metric, "date": "$date", "run_id": "$_id"}},
            }
        },
    ]

    aggregate_result = adapter.flowcells_aggregate(pipe)
    for result in aggregate_result:
        group = result["_id"]["instrument"]
        for plot_name in LANE_UDFS:
            data_tuples = [(d["date"], d["run_id"], d.get(plot_name)) for d in result["data"]]
            data_sorted = sorted(data_tuples)
            data = []
            for date, run_id, value in data_sorted:
                if value:
                    data.append([date, value, run_id])
            if data:
                instruments["data"][plot_name][group] = {"data": data}
    return instruments
