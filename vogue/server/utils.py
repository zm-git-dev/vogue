#!/usr/bin/env python

from mongo_adapter import get_client
from extentions import adapter
from datetime import datetime as dt
import numpy as np

MONTHS = [(1, 'Jan'), (2, 'Feb'), (3, 'Mar'), (4, 'Apr'), 
        (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), 
        (10, 'Oct'), (11, 'Nov'), (12, 'Dec')]


COLORS = [('RGB(128, 128, 128)','RGB(128, 128, 128, 0.2)'),('RGB(255, 0, 0)','RGB(255, 0, 0, 0.2)'),
          ('RGB(0, 128, 128)','RGB(0, 128, 128, 0.2)'),('RGB(128, 0, 128)','RGB(128, 0, 128, 0.2)'),
          ('RGB(128, 0, 0)','RGB(128, 0, 0,0.2)'), ('RGB(128, 128, 0)','RGB(128, 128, 0,0.2)'),
          ('RGB(52, 152, 219)', 'RGB(52, 152, 219, 0.2)'),('RGB(33, 97, 140)','RGB(33, 97, 140, 0.2)'),  
          ('RGB(46, 204, 113)','RGB(46, 204, 113, 0.2)'),('RGB(241, 196, 15)','RGB(241, 196, 15, 0.2)'),
          ('RGB(23, 32, 42)','RGB(23, 32, 42, 0.2)'),('RGB(183, 149, 11)','RGB(183, 149, 11, 0.2)'),  
          ('RGB(0, 255, 0)','RGB(0, 255, 0, 0.2)'),('RGB(0, 255, 255)','RGB(0, 255, 255, 0.2)'),
          ('RGB(255, 0, 255)','RGB(255, 0, 255, 0.2)'),('RGB(0, 0, 255)','RGB(0, 0, 255, 0.9)')]



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
        a = np.array(values)
        percentiles = [np.percentile(a,25), np.percentile(a,50), np.percentile(a,72)]

    return percentiles


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
                query[group_key] = group
            if y_axis_key:
                query[y_axis_key] = {'$exists' : True}
            print(query)
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
                group_has_any_valid_data = True
        if group_has_any_valid_data:
            defrosts['data'][group] = {'median' : median,'quartile': quartile, 'color' : COLORS[i]}
            
    return defrosts


def scatter_to_remoove_find(year : int= None, adapter = adapter)-> dict:
    """Prepares data for ... plots."""

    group_by_key = 'lotnr'
    date1, date2 = get_dates_of_year(int(year))
    group_by = list(adapter.sample_collection.distinct(group_by_key))
    defrosts = {'axis' : {'x' : 'Number of Defrosts', 'y' : 'Concentration (nM)'}, 
                'data': {}, 'title' : 'wgs illumina PCR-free'}
    for i, group in enumerate(group_by):
        data = []
        query = {'lotnr' : group, 
                'received_date' : {'$gte' : date1, '$lt' : date2},
                'nr_defrosts-concentration' : { '$exists' : True},
                'nr_defrosts': { '$exists' : True}}
        samples = adapter.find_samples(query)
        for sample in samples:
            data.append({'x' : sample['nr_defrosts'], 'y': round(sample['nr_defrosts-concentration'], 2), 
                        'name': sample['_id']})
        if data:
            defrosts['data'][group] = {'data' : data, 'color' : COLORS[i]}
 
    return defrosts
