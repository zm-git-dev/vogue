import numpy as np
from vogue.constants.constants import TEST_SAMPLES


def pipe_value_per_month(year: int, y_val: str, group_key: str = None) -> list:
    """Build aggregation pipeline to get information for a plot from the sample colection.

    A plot is going to show some average value (determined by y_val) per month,
    grouped by some group (determined by group_key). And it will only show
    data from a specific year (determined by year). If y_val='count' the value on the y-axis
    will instead be nr per samples.

    Arguments:
        year(int):      Any year.
        y_val(str):     A key (of a sample document) that we want to plot. Or 'count'
        group_key(str): A key (of the sample document) on wich we want to group. Can be None!

    eg 1:
        y_val = 'library_size_post_hyb'
        year = 2018
        group_key = 'source'

        Plot content:
            Average library_size_post_hyb/month for all samples during 2018 grouped by source

    eg 2:
        y_val = 'count'
        year = 2017
        group_key = 'priority'

        Plot content:
            Number of revieved samples/month during 2017 grouped by priority.
    """

    match = {"$match": {"received_date": {"$exists": True}, "_id": {"$nin": TEST_SAMPLES}}}
    project = {
        "$project": {"month": {"$month": "$received_date"}, "year": {"$year": "$received_date"}}
    }
    match_year = {"$match": {"year": {"$eq": year}}}
    group = {"$group": {"_id": {"month": "$month"}}}
    sort = {"$sort": {"_id.month": 1}}

    if group_key:  # grouping by group_key
        match["$match"][group_key] = {"$exists": True}
        project["$project"][group_key] = 1
        group["$group"]["_id"][group_key] = "$" + group_key
        sort["$sort"]["_id." + group_key] = 1

    if y_val == "count":
        # count nr samples per month:
        group["$group"][y_val] = {"$sum": 1}
    else:
        # get average of y_val:
        match["$match"][y_val] = {"$exists": True}
        project["$project"][y_val] = 1
        group["$group"][y_val] = {"$push": "$" + y_val}

    return [match, project, match_year, group, sort]


def value_per_month(adapter, year: int, y_val: str, group_key: str = None):
    """Wraper function that will build a pipe, aggregate results from database and
    prepare the data for the plot."""

    pipe = pipe_value_per_month(year, y_val, group_key)
    aggregate_result = adapter.samples_aggregate(pipe)
    return reformat_aggregate_results(list(aggregate_result), y_val, group_key)


def reformat_aggregate_results(aggregate_result, y_val, group_key=None):
    """Reformats raw output from the aggregation query to the format required by the plots.

    Arguments:
        aggregate_result (list): output from aggregation query.
        y_val(str):   A key (of a sample document) that we want to plot. Or 'count'
        group_key(str): A key (of the sample document) on wich we want to group. Can be None!
    Returns:
        plot_data(dict): see example

    Example:
        aggregate_result:
        [{'_id': {'strain': 'A. baumannii', 'month': 1}, 'microbial_library_concentration': 21.96},
         {'_id': {'strain': 'A. baumannii', 'month': 3}, 'microbial_library_concentration': 43.25},
         ...,
         {'_id': {'strain': 'E. coli', 'month': 2}, 'microbial_library_concentration': 7.68},
         ...]

        plot_data: {'A. baumannii': {'data': [21.96, None, 43.25,...]},
                    'E. coli': {'data': [None, 7.68, ...]},
                                            ...}
    """

    plot_data = {}
    for group in aggregate_result:
        if group_key:
            group_name = group["_id"][group_key]
        else:
            group_name = "all_samples"
        month = group["_id"]["month"]
        if y_val == "count":
            value = group[y_val]
        else:
            value = np.mean([float(val) for val in group[y_val]])

        if group_name not in plot_data:
            plot_data[group_name] = {"data": [None] * 12}
        plot_data[group_name]["data"][month - 1] = value
    return plot_data
