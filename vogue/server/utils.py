#!/usr/bin/env python

from mongo_adapter import get_client
from datetime import datetime as dt
import numpy as np
from vogue.constants.constants import (MONTHS, TEST_SAMPLES)


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

    if group_key: # grouping by group_key
        match['$match'][group_key] = {'$exists' : True}
        project['$project'][group_key] = 1
        group['$group']['_id'][group_key] = '$' + group_key
        sort['$sort']['_id.' + group_key] =  1
    
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
        {'microbial_library_concentration': {'A. baumannii': {'data': [21.96, None, 43.25,...]},
                                            'E. coli': {'data': [None, 7.68, ...]},
                                            ...}
        """

    results_reformated = {}
    for plot in y_vals:
        plot_data = {}
        for group in aggregate_result: 
            if group_key:
                group_name = group['_id'][group_key]
            else:
                group_name = 'all_samples'
            month = group['_id']['month']
            value = group[plot]

            if group_name not in plot_data:
                plot_data[group_name] = {'data' : [None]*12}
            plot_data[group_name]['data'][month -1] = value

        results_reformated[plot] = plot_data
    return results_reformated

def value_per_month(adapter, year: str, y_vals: list, group_key: str = None):
    """Wraper function that will build a pipe, aggregate results from database and 
    prepare the data for the plots."""

    pipe = pipe_value_per_month(int(year), y_vals, group_key)
    aggregate_result = adapter.samples_aggregate(pipe)
    return reformat_aggregate_results(list(aggregate_result), y_vals, group_key)

def plot_attributes( y_axis_label: str = '', title: str = '', x_axis_label: str = ''):
    """Prepares some plot atributes general for plots showing some data per month.

    Arguments:
        y_axis_label(str): eg. 'Concentration (nM)' or 'Days' 
        title(str): Title of the plot."""

    return {'axis' : {'y' : y_axis_label, 'x' : x_axis_label}, 
            'title' : title, 
            'labels' : [m[1] for m in MONTHS]}


def find_concentration_amount(adapter, year : int = None)-> dict:
    """Prepares data for a scatter plot showning Concentration agains Amount."""

    amount = {'data': []}
    pipe = [{'$match': {
                'received_to_delivered': {'$exists': True}, 
                'amount': {'$exists': True}, 
                'amount-concentration': {'$exists': True}}
                }, {
            '$project': {
                'year': {'$year': '$received_date'}, 
                'amount': 1, 
                'amount-concentration': 1}
                }, {
            '$match': {
                'year': {'$eq': int(year)}
                }
            }]

    aggregate_result = adapter.samples_aggregate(pipe)
    for sample in aggregate_result:
        if sample['amount']>200:
            sample['amount'] = 200
        amount['data'].append({'x' : sample['amount'], 'y': round(sample['amount-concentration'], 2), 
                                'name': sample['_id'] })
    return amount

def find_concentration_defrosts(adapter, year : int)-> dict:
    """Prepares data for a plot showning Number of defrosts against Concentration"""

    nr_defrosts = list(adapter.sample_collection.distinct('nr_defrosts'))
    defrosts = {'axis' : {'x' : 'Number of Defrosts', 'y' : 'Concentration (nM)'}, 
                'data': {}, 'title' : 'wgs illumina PCR-free', 'labels':nr_defrosts.sort()}

    pipe = [{'$match': {
                'received_to_delivered': {'$exists': True}, 
                'nr_defrosts-concentration': {'$exists': True}, 
                'nr_defrosts': {'$exists': True}, 
                'lotnr': {'$exists': True}}
            }, {
            '$project': {
                'year': {'$year': '$received_date'}, 
                'nr_defrosts-concentration': 1, 
                'nr_defrosts': 1, 
                'lotnr': 1}
            }, {
            '$match': {
                'year': {'$eq': int(year)}}
            }, {
            '$group': {
                '_id': {
                    'nr_defrosts': '$nr_defrosts', 
                    'lotnr': '$lotnr'}, 
                'count': {'$sum': 1}, 
                'values': {'$push': '$nr_defrosts-concentration'}}
            }, {
            '$sort': {'_id.nr_defrosts': 1}
            }]
    aggregate_result = adapter.samples_aggregate(pipe)

    for result in aggregate_result:
        group = result['_id']['lotnr']        
        if group not in defrosts['data']:
            defrosts['data'][group] = {'median' : [],'quartile': [], 'nr_samples' : []}
        nr = result['_id']['nr_defrosts']
        values = np.array(result['values'])
        defrosts['data'][group]['median'].append([nr, round(np.percentile(values,50), 2)])
        defrosts['data'][group]['quartile'].append([nr, round(np.percentile(values,25),2), round(np.percentile(values,75),2)])
        defrosts['data'][group]['nr_samples'].append([nr, result['count']])
            
    return defrosts


def q30_instruments(adapter, year : int)-> dict:
    """Prepares data for a plot Q30 values for diferent runs over time"""

    instruments = {'axis' : {'y' : 'Average Q30'}, 
                'data': {}, 'title' : 'Q30'}
    pipe=[{
        '$project': {
            'year': {'$year': '$date'}, 
            'instrument': 1, 
            'date': 1, 
            'avg': 1}
        }, {
        '$match': {'year': {'$eq': int(year)}}
        }, {
        '$group': {'_id': {'instrument': '$instrument'}, 
                    'data': {'$push': {
                    'Q30': '$avg.% Bases >=Q30', 
                    'date': '$date', 
                    'run_id': '$_id'}}}}]

    aggregate_result = adapter.flowcells_aggregate(pipe)
    for result in aggregate_result:
        group = result['_id']['instrument'] 
        data_tuples = [(d['date'], d['run_id'], d.get('Q30')) for d in result['data']]
        data_sorted = sorted(data_tuples)
        data = []
        for date, run_id, Q30 in data_sorted:
            if Q30:
                data.append([date, Q30, run_id])
        if data:
            instruments['data'][group] = {'data':data}

    return instruments
