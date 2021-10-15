from statistics import mean


def reagent_category_data(
    adapter, index_category: str, flowcell_performance_treshold: float
) -> dict:
    """Preraring data for index performance view grouped on reagent label category"""

    pipe = (
        [
            {
                "$lookup": {
                    "from": "reagent_label_category",
                    "localField": "index",
                    "foreignField": "_id",
                    "as": "index_category",
                }
            },
            {"$match": {"index_category.category": index_category}},
        ]
        + _normalized_performance_pipe(flowcell_performance_treshold)
        + [
            {
                "$project": {
                    "_id": "$_id.index",
                    "avg_performance": {"$avg": "$normalized_index_performance"},
                    "nr_runs": {"$size": "$normalized_index_performance"},
                }
            }
        ]
    )

    aggregate_result = adapter.reagent_label_aggregate(pipe)

    average_normalized_peformance = []

    for data in aggregate_result:
        average_normalized_peformance.append(
            {
                "name": data["_id"],
                "y": data["avg_performance"],
                "nr_runs": data["nr_runs"],
            }
        )
    return average_normalized_peformance


def reagent_label_data(adapter, index: str, flowcell_performance_treshold: float) -> list:
    """Preraring data for index performance view grouped on reagent label"""

    pipe = [{"$match": {"index": {"$eq": index}}}] + _normalized_performance_pipe(
        flowcell_performance_treshold
    )

    aggregate_result = list(adapter.reagent_label_aggregate(pipe))

    if not aggregate_result:
        return []

    performance = aggregate_result[0]["normalized_index_performance"]
    flowcells = aggregate_result[0]["flowcell_id"]

    normalized_peformance = list(map(lambda x, y: [x, y], flowcells, performance))
    return normalized_peformance


def _normalized_performance_pipe(flowcell_performance_treshold) -> list:
    """Mongo aggregation pipe to get normalized index performance."""

    return [
        {
            "$match": {
                "flowcell_target_reads": {"$exists": "True", "$ne": None, "$gt": 0},
                "flowcell_total_reads": {"$exists": "True", "$ne": None, "$gt": 0},
                "index_target_reads": {"$exists": "True", "$ne": None, "$gt": 0},
                "index_total_reads": {"$exists": "True", "$ne": None, "$gt": 1000},
                "flowcell_id": {"$exists": "True"},
            }
        },
        {
            "$project": {
                "flowcell_id": 1,
                "index_performance": {"$divide": ["$index_total_reads", "$index_target_reads"]},
                "flowcell_performance": {
                    "$divide": ["$flowcell_total_reads", "$flowcell_target_reads"]
                },
                "index": 1,
            }
        },
        {
            "$project": {
                "normalized_index_performance": {
                    "$divide": ["$index_performance", "$flowcell_performance"]
                },
                "flowcell_id": 1,
                "flowcell_performance": 1,
                "index": 1,
            }
        },
        {"$match": {"flowcell_performance": {"$gt": flowcell_performance_treshold}}},
        {
            "$group": {
                "_id": {"index": "$index"},
                "normalized_index_performance": {"$push": "$normalized_index_performance"},
                "flowcell_performance": {"$push": "$flowcell_performance"},
                "flowcell_id": {"$push": "$flowcell_id"},
            }
        },
    ]
