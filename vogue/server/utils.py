#!/usr/bin/env python

from mongo_adapter import get_client
from extentions import adapter
from datetime import datetime as dt
import numpy as np
from vogue.constants.constants import MONTHS, COLORS


def get_dates_of_month(month: int, year: int)-> list:
    """Returns:
        date1 = first date of month (datetime) 
        date2 = first date of next month (datetime) """

    date1 = dt(year, month, 1, 0, 0)
    if month == 12:
        date2 = dt(year + 1, 1, 1, 0, 0)
    else:
        date2 = dt(year, month +1 , 1, 0, 0)

    return date1, date2

def get_dates_of_year(year: int)-> list:
    """Returns:
        date1 = first jan 'this' year
        date2 = first jan 'next' year """

    date1 = dt(year, 1, 1, 0, 0)
    date2 = dt(year + 1, 1, 1, 0, 0)

    return date1, date2

def get_average(samples: list, key: str)-> float:
    """Calculates the averages of the key value for all samples."""

    values = []
    average = None
    for sample in samples:
        value = sample.get(key)
        if isinstance(value, int) or isinstance(value, float):
            values.append(value)
    if values:
        average = sum(values) / float(len(values))

    return average

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


def build_apptag_group_queries()-> list:
    categories = adapter.app_tag_collection.distinct('category')
    apptag_group_queries = {}
    for category in categories:
        app_tags = list(adapter.find_app_tags({'category' : category}))
        group = [tag.get('_id') for tag in app_tags] 
        apptag_group_queries[category] = {'application_tag': {'$in' : [group] }}
    return apptag_group_queries



def build_sample_groups()-> dict:
    categories = adapter.app_tag_collection.distinct('category')
    sample_groups = {}
    for category in categories:
        app_tags = list(adapter.find_app_tags({'category' : category}))
        app_tags = [tag.get('_id') for tag in app_tags] 
        query = {'application_tag': {'$in' : app_tags }}
        sample_groups[category] = list(adapter.find_samples(query))
    return sample_groups


def build_group_queries_from_key(group_key)-> list:
    group_by = list(adapter.sample_collection.distinct(group_key))


def find_key_over_time( title: str = None, year : int = None, group_key: str = None, 
                        y_axis_key: str = None, y_axis_label: str = None, y_unit : str = None, 
                        adapter = adapter)-> dict:

    """Prepares data for plots showing progress of "something" over "time".

    The "time" is allways in months and the "something" can be either number of samples of a 
    certain group, or the average of some value from all samples within a certain group.
    If no group_key is provided, all samples will be concidered as one group.

    Input:
        title :         Plot title.
        year :          Data from this year will be shown in the plot. 
        group_key :     Is the key in the database holding the group value.
        y_axis_key :    Key in database wich value will be plotted on the Y-axes (if given).
        y_unit :        Determines what to plot on the y axis (average/nr samples) (if "nr samples", 
                        no y_axis_key is needed).
        y_axis_label :  What it seems to be :)
        """
    groups = build_sample_groups()
    print(groups)

    if group_key:
        group_by = list(adapter.sample_collection.distinct(group_key))
    else: 
        group_by = ['no_group']

    plot_content = {'axis' : {'y' : y_axis_label}, 
                    'group' : {}, 
                    'title' : title, 
                    'labels' : [m[1] for m in MONTHS]}

    for i, group in enumerate(group_by):
        data = []
        for month_number, month_name in MONTHS:

            date1, date2 = get_dates_of_month(month_number, int(year))
            query = {'received_date' : {'$gte' : date1, '$lt' : date2}}

            if group_key:
                query[group_key] = { '$in' : [group] } 
            if y_axis_key:
                query[y_axis_key] = {'$exists' : True}
            samples = list(adapter.find_samples(query))

            if y_unit == 'number samples':
                y = len(samples)
            elif y_unit == 'average':
                average = get_average(samples, y_axis_key)
                y = round(average,1) if average else None

            if y:
                data.append(y)
            else:
                data.append(None)

        if list(set(data)) != [None]:
            plot_content['group'][group] = {'data' : data, 'color' : COLORS[i]}      

    return plot_content


def find_concentration_amount(year : int = None, adapter = adapter)-> dict:
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

def find_concentration_defrosts(year : int = None, adapter = adapter)-> dict:
    """Prepares data for a plot showning Number of defrosts agains Concentration"""

    group_by_key = 'lotnr'
    date1, date2 = get_dates_of_year(int(year))
    group_by = list(adapter.sample_collection.distinct(group_by_key))
    nr_defrosts = list(adapter.sample_collection.distinct('nr_defrosts'))
    nr_defrosts.sort()

    defrosts = {'axis' : {'x' : 'Number of Defrosts', 'y' : 'Concentration (nM)'}, 
                'data': {}, 'title' : 'wgs illumina PCR-free', 'labels':nr_defrosts}

    for i, group in enumerate(group_by):
        group_has_any_valid_data = False
        median = []
        quartile = []
        nr_samples = []
        for nr in nr_defrosts:
            query = {'lotnr' :  group, 
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
            
    return defrosts
