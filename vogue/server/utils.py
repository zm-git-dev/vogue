#!/usr/bin/env python

from mongo_adapter import get_client
from datetime import datetime as dt

MONTHS = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), 
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), 
        (10, 'October'), (11, 'November'), (12, 'December')]


COLORS = [('RGB(128, 128, 128)','RGB(128, 128, 128, 0.2)'),('RGB(255, 0, 0)','RGB(255, 0, 0, 0.2)'),
        ('RGB(0, 128, 128)','RGB(0, 128, 128, 0.2)'),('RGB(128, 0, 128)','RGB(128, 0, 128, 0.2)'),
        ('RGB(128, 0, 0)','RGB(128, 0, 0,0.2)'), ('RGB(128, 128, 0)','RGB(128, 128, 0,0.2)'),
        ('RGB(52, 152, 219)', 'RGB(52, 152, 219, 0.2)'),('RGB(33, 97, 140)','RGB(33, 97, 140, 0.2)'),  
         ('RGB(46, 204, 113)','RGB(46, 204, 113, 0.2)'),('RGB(241, 196, 15)','RGB(241, 196, 15, 0.2)'),
         ('RGB(23, 32, 42)','RGB(23, 32, 42, 0.2)'),('RGB(183, 149, 11)','RGB(183, 149, 11, 0.2)'),  
        ('RGB(0, 255, 0)','RGB(0, 255, 0, 0.2)'),('RGB(0, 255, 255)','RGB(0, 255, 255, 0.2)'),
        ('RGB(255, 0, 255)','RGB(255, 0, 255, 0.2)'),('RGB(0, 0, 255)','RGB(0, 0, 255, 0.2)')]



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


def find_recived_per_month(year : int, group_by : list, group_key : str, adapter)-> dict:
    """Prepares data for recived_per_month plots.
    Input:
        group_by: the data in the plot will be grouped by the the values in this list.
        group_key: is the key in the database holding the group value."""

    data = {}
    for i, group in enumerate(group_by):
        data[group] = {'data' : {'labels':[], 'X' : [], 'Y' : []}, 'color' : COLORS[i]}
        for month_number, month_name in MONTHS:
            date1, date2 = get_dates_of_month(month_number, int(year))
            query = {group_key : group, 
                    'received_date' : {'$gte' : date1, '$lt' : date2}}
            samples = adapter.find_samples(query)
            data[group]['data']['labels'].append(month_name)
            data[group]['data']['X'].append(month_number)
            data[group]['data']['Y'].append(len(samples))

    return data


def turn_around_times(year : int, group_by : list, group_key : str, time_range_key : str, 
                        adapter)-> dict:
    """Prepares data for turn_around_time plots.
    Input:
        group_by: the data in the plot will be grouped by the the values in this list.
        group_key: is the key in the database holding the group value.
        time_range_key: The key in the database holding the timerange value (in #days) to plot"""

    data = {}
    for i, group in enumerate(group_by):
        data[group] = {'data' : {'labels':[], 'X' : [], 'Y' : []}, 'color' : COLORS[i]}
        for month_number, month_name in MONTHS:
            date1, date2 = get_dates_of_month(month_number, int(year))
            query = {group_key : group, 
                    'received_date' : {'$gte' : date1, '$lt' : date2}}
            samples = list(adapter.find_samples(query))
            average = get_average(samples, time_range_key)
            if average:
                data[group]['data']['labels'].append(month_name)
                data[group]['data']['X'].append(month_number)
                data[group]['data']['Y'].append(average)

    return data


def find_concentration_defrosts(year : int, adapter)-> dict:
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
            data.append({'x' : sample['nr_defrosts'], 'y': round(sample['nr_defrosts-concentration'], 2) })
        if data:
            defrosts['data'][group] = {'data' : data, 'color' : COLORS[i]}
 
    return defrosts


def find_concentration_amount(year : int, adapter)-> dict:
    """Prepares data for ... plots."""

    date1, date2 = get_dates_of_year(int(year))
    amount = {'axis' : {'x' : 'Amount (ng)', 'y' : 'Concentration (nM)'}, 
                'data': [], 'title' : 'lucigen PCR-free'}
    query = {'received_date' : {'$gte' : date1, '$lt' : date2},
                'amount' : { '$exists' : True},
                'amount-concentration': { '$exists' : True}}

    samples = adapter.find_samples(query)
    for sample in samples:
        amount['data'].append({'x' : sample['amount'], 'y': round(sample['amount-concentration'], 2), 'label': sample['_id'] })

    return amount



def find_key_over_time(year : int, group_by_key: str, y_axis_key: str, title: str, y_axis_label: str,adapter)-> dict:
    """Prepares"""

    group_by = list(adapter.sample_collection.distinct(group_by_key))
    concentration_time = {'axis' : {'x' : 'Time', 'y' : y_axis_label}, 
                'data': {}, 'title' : title, 'labels' : [m[1] for m in MONTHS]}

    for i, group in enumerate(group_by):
        data = []
        for month_number, month_name in MONTHS:
            date1, date2 = get_dates_of_month(month_number, int(year))
            query = {group_by_key : group, 
                    'prepared_date' : {'$gte' : date1, '$lt' : date2},
                    y_axis_key : { '$exists' : True}}

            samples = list(adapter.find_samples(query))
            average = get_average(samples, y_axis_key)
            if average:
                data.append({'x' : month_name, 'y': round(average, 2) })

        if data:
            concentration_time['data'][group] = {'data' : data, 'color' : COLORS[i]}
    return concentration_time


# ###################
# def find_key_over_time_other(year : int, group_by_key: str, y_axis_key: str, title: str, y_axis_label: str, 
#                     adapter, by_month: bool = True)-> dict:
#     """Prepares""" ##OBS THIS ONE IS A BIG QUESTON MARK. WHEN WE SAY OVER TIME HERE, HOW DO WE MESRE TIME? 
#     # received_date IS OBVOIUSLY NOT THE CORRECT DATE TO LOOK AT....

#     group_by = list(adapter.sample_collection.distinct(group_by_key))
#     labels = [m[1] for m in MONTHS] if by_month else [m[0] for m in MONTHS]
#     concentration_time = {'axis' : {'x' : '# Months', 'y' : y_axis_label}, 
#                 'data': {}, 'title' : title, 'labels' : labels}
#     for i, group in enumerate(group_by):
#         data = []
#         first_time = None
#         for month_number, month_name in MONTHS:
#             date1, date2 = get_dates_of_month(month_number, int(year))
#             query = {group_by_key : group, 
#                     'prepared_date' : {'$gte' : date1, '$lt' : date2},
#                     y_axis_key : { '$exists' : True}}

#             samples = list(adapter.find_samples(query))
#             average = get_average(samples, y_axis_key)
            
#             if average:
#                 if not first_time:
#                     first_time = month_number
#                 if by_month:
#                     data.append({'x' : month_number , 'y': round(average, 2) })
#                 else:
#                     data.append({'x' : month_number - first_time + 1, 'y': round(average, 2) })

#         if data:
#             print(data)
#             concentration_time['data'][group] = {'data' : data, 'color' : COLORS[i]}
#     return concentration_time