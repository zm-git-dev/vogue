#!/usr/bin/env python

from mongo_adapter import get_client
from datetime import datetime as dt
import numpy as np
from vogue.constants.constants import MONTHS, COLORS, TEST_SAMPLES


def get_dates_of_year(year: int)-> list: # TO BE REMOVED
    """Returns:
        date1 = first jan 'this' year
        date2 = first jan 'next' year """

    date1 = dt(year, 1, 1, 0, 0)
    date2 = dt(year + 1, 1, 1, 0, 0)

    return date1, date2


def get_percentiles(samples: list, key: str)-> float:
    """Calculates percentiles of the key value for all samples."""

    values = []
    percentiles = []
    for sample in samples:
        value = sample.get(key)
        if isinstance(value, int) or isinstance(value, float):
            values.append(value)
    if values:
        values = np.array(values)
        percentiles = [np.percentile(values,25), np.percentile(values,50), np.percentile(values,75)]

    return percentiles


def pipe_value_per_month(year: int, y_vals: list, group_key: str = None)-> list:
    """Build aggregation pipeline to get information for one or more plots.

    A plot is going to show some value (determined by y_vals) per month, 
    grouped by some group (determined by group_key). And it will only show 
    data from a specific year (determined by year).

    The number of values in the list y_vals, is the number of plots that we are preparing data for.
     
    Arguments:
        year(int):      Any year.
        y_vals(list):   A list of keys (of a sample document) that we want to plot.
                        The list can also contain the element: 'count'.
        group_key(str): A key (of the sample document) on wich we want to group. Can be None!

    eg:  
        y_vals = ['library_size_post_hyb', 'count'] 
        year = 2018
        group_key = 'source'
        
        will prepare data for two plots. 
            1) The average library_size_post_hyb/month for all samples during 2018 grouped by source
            2) Number of revieved samples/month during 2018 grouped by source. """

    if group_key: # grouping by month and group_key
        match = {'$match':{
                    'received_date' : {'$exists' : True},
                    '_id' : {'$nin' : TEST_SAMPLES},
                    group_key : {'$exists' : True}
                    }}
        project = {'$project': {
                    'month' : {'$month' : '$received_date'}, 
                    'year' : {'$year' : '$received_date'},  
                    group_key : 1
                    }}
        match_year = {'$match': {
                        'year': {'$eq': year}
                        }}
        group = {'$group': {'_id': {
                                group_key : '$' + group_key, 
                                'month': '$month'}
                    }}
        sort = {'$sort': {
                    '_id.' + group_key: 1, 
                    '_id.month': 1
                    }}
    else: # grouping only by month
        match = {'$match':{
                    'received_date' : {'$exists' : True},
                    '_id' : {'$nin' : TEST_SAMPLES}
                    }}
        project = {'$project': {
                    'month' : {'$month' : '$received_date'}, 
                    'year' : {'$year' : '$received_date'}
                    }}
        match_year = {'$match': {
                        'year': {'$eq': year}
                        }}
        group = {'$group': {
                '_id': {'month': '$month'}
                }}
        sort = {'$sort': {
                    '_id.month': 1
                    }}
    
    for y_val in y_vals:
        if y_val == 'count':
            # count nr samples per month:
            group['$group'][y_val] = {'$sum': 1}
        else:
            # get average of y_val:
            project['$project'][y_val] = 1
            group['$group'][y_val] = {'$avg': '$' + y_val}
 
    return [match, project, match_year, group, sort]
    
def reformat_aggregate_results(aggregate_result, y_vals, group_key = None):
    """Reformats raw output from the aggregation query to the format required by the plots.
    
    Arguments:
        aggregate_result (list): output from aggregation query.
        y_vals(list):   A list of keys (of a sample document) that we want to plot.
                        The list can also contain the element: 'count'.
        group_key(str): A key (of the sample document) on wich we want to group. Can be None!
    Returns:
        results_reformated (dict): see example   
        
    Example: 
        aggregate_result: 
        [{'_id': {'strain': 'A. baumannii', 'month': 1}, 'microbial_library_concentration': 21.96}, 
         {'_id': {'strain': 'A. baumannii', 'month': 3}, 'microbial_library_concentration': 43.25},
         ...,
         {'_id': {'strain': 'E. coli', 'month': 2}, 'microbial_library_concentration': 7.68},
         ...]
    
        results_reformated:
        {'microbial_library_concentration': {'A. baumannii': {'data': [21.96, None, 43.25,...],
                                                              'color': ('RGB(33, 97, 140)', 
                                                                        'RGB(33, 97, 140, 0.2)},
                                            'E. coli': {'data': [None, 7.68, ...],
                                                        'color': ('RGB(0, 0, 255)', 
                                                                   'RGB(0, 0, 255, 0.9)')},
                                            ...}
        """

    results_reformated = {}
    for plot in y_vals:
        plot_data = {}
        i = 0
        for group in aggregate_result: 
            if group_key:
                group_name = group['_id'][group_key]
            else:
                group_name = 'all_samples'
            month = group['_id']['month']
            value = group[plot]

            if group_name not in plot_data:
                plot_data[group_name] = {'data' : [None]*12, 'color' : COLORS[i]}
                i=0 if i==len(COLORS)-1 else i+1
            plot_data[group_name]['data'][month -1] = value

        results_reformated[plot] = plot_data
    return results_reformated

def value_per_month(adapter, year: str, y_vals: list, group_key: str = None):
    """Wraper function that will build a pipe, aggregate results from database and 
    prepare the data for the plots."""

    pipe = pipe_value_per_month(int(year), y_vals, group_key)
    aggregate_result = adapter.samples_aggregate(pipe)
    return reformat_aggregate_results(list(aggregate_result), y_vals, group_key)

def plot_atributes( y_axis_label: str, title: str):
    """Prepares some plot atributes"""
    return {'axis' : {'y' : y_axis_label}, 
            'title' : title, 
            'labels' : [m[1] for m in MONTHS]}

def find_concentration_amount(adapter, year : int = None)-> dict:
    """Prepares data for a scatter plot showning Concentration agains Amount."""

    date1, date2 = get_dates_of_year(int(year))
    amount = {'axis' : {'x' : 'Amount (ng)', 'y' : 'Concentration (nM)'}, 
                'data': [], 'title' : 'lucigen PCR-free'}
    query = {'received_date' : {'$gte' : date1, '$lt' : date2},
                'amount' : { '$exists' : True},
                'amount-concentration': { '$exists' : True}}

    samples = adapter.find_samples(query)
    for sample in samples:
        if sample['amount']>200:
            sample['amount'] = 200
        amount['data'].append({'x' : sample['amount'], 'y': round(sample['amount-concentration'], 2), 
                                'name': sample['_id'] })

    return amount

def find_concentration_defrosts(adapter, year : int = None)-> dict:
    """Prepares data for a plot showning Number of defrosts agains Concentration"""

    group_by_key = 'lotnr'
    date1, date2 = get_dates_of_year(int(year))
    group_by = list(adapter.sample_collection.distinct(group_by_key))
    nr_defrosts = list(adapter.sample_collection.distinct('nr_defrosts'))
    nr_defrosts.sort()

    defrosts = {'axis' : {'x' : 'Number of Defrosts', 'y' : 'Concentration (nM)'}, 
                'data': {}, 'title' : 'wgs illumina PCR-free', 'labels':nr_defrosts}

    i = 0
    for group in group_by:
        group_has_any_valid_data = False
        median = []
        quartile = []
        nr_samples = []
        for nr in nr_defrosts:
            query = {'lotnr' : group, 
                'received_date' : {'$gte' : date1, '$lt' : date2},
                'nr_defrosts-concentration' : { '$exists' : True},
                'nr_defrosts': { '$eq' : nr}}
            samples = list(adapter.find_samples(query))
            percentiles = get_percentiles(samples, 'nr_defrosts-concentration')
            if percentiles:
                median.append([nr ,round(percentiles[1], 2)])
                quartile.append([nr, round(percentiles[0], 2), round(percentiles[2], 2)])
                nr_samples.append(len(samples))
                group_has_any_valid_data = True
        if group_has_any_valid_data:
            defrosts['data'][group] = {'median' : median,'quartile': quartile, 'color' : COLORS[i], 
                                        'nr_samples' : nr_samples}
            i=0 if i==len(COLORS)-1 else i+1
            
    return defrosts
