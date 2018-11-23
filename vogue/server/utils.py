#!/usr/bin/env python

from mongo_adapter import get_client
from datetime import datetime as dt

#from vogue.adapter.adapter import VougeAdapter
#client = get_client(uri = "mongodb://localhost:27017")
#adapter = VougeAdapter(client, db_name = 'trending')



MONTHS = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

COLORS = [('RGB(128, 128, 128)','RGB(128, 128, 128, 0.2)'),('RGB(255, 0, 0)','RGB(255, 0, 0, 0.2)'),
        ('RGB(0, 128, 128)','RGB(0, 128, 128, 0.2)'),('RGB(128, 0, 128)','RGB(128, 0, 128, 0.2)'),
        ('RGB(128, 0, 0)','RGB(128, 0, 0,0.2)'), ('RGB(128, 128, 0)','RGB(128, 128, 0,0.2)')]



def get_dates(month, year):
    date1 = dt(year, month, 1, 0, 0)
    if month == 12:
        date2 = dt(year + 1, 1, 1, 0, 0)
    else:
        date2 = dt(year, month +1 , 1, 0, 0)

    return date1, date2

def get_average(samples, key):
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
    data = {}
    months = list(range(1,13))
    #group_by = ['research', 'diagnostic','standard']
    #group_key = "priority"
    for i, group in enumerate(group_by):
        data[group] = {'data' : {'labels':[], 'X' : [], 'Y' : []}, 'color' : COLORS[i]}
        for month in months:
            date1, date2 = get_dates(month, int(year))
            query = {group_key : group, 
                    "received_date" : {"$gte" : date1, "$lt" : date2}}
            samples = adapter.find_samples(query)
            data[group]['data']['labels'].append(MONTHS[month])
            data[group]['data']['X'].append(month)
            data[group]['data']['Y'].append(len(samples))
    return data


def turn_around_times(year : int, group_by : list, group_key : str, time_range_key : str, adapter)-> dict:
    data = {}
    months = list(range(1,13))
    for i, group in enumerate(group_by):
        data[group] = {'data' : {'labels':[], 'X' : [], 'Y' : []}, 'color' : COLORS[i]}
        for month in months:
            date1, date2 = get_dates(month, int(year))
            query = {group_key : group, 
                    "received_date" : {"$gte" : date1, "$lt" : date2}}
            samples = list(adapter.find_samples(query))
            average = get_average(samples, time_range_key)
            if average:
                data[group]['data']['labels'].append(MONTHS[month])
                data[group]['data']['X'].append(month)
                data[group]['data']['Y'].append(average)
    return data





    

