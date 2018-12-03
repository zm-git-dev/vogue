#!/usr/bin/env python

from cgface import api
from datetime import date

cg = api.CgFace()

MONTHS = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]
COLORS = [('RGB(128, 128, 128)','RGB(128, 128, 128, 0.2)'),('RGB(255, 0, 0)','RGB(255, 0, 0, 0.2)'),
        ('RGB(0, 128, 128)','RGB(0, 128, 128, 0.2)'),('RGB(128, 0, 128)','RGB(128, 0, 128, 0.2)'),
        ('RGB(128, 0, 0)','RGB(128, 0, 0,0.2)'), ('RGB(128, 128, 0)','RGB(128, 128, 0,0.2)')]


class PrepsCommon():

    def __init__(self, year):
        self.year = str(year)

    def make_data(self, data_type):
        nr_samples_per_month = cg.trends('samples',self.year, key=data_type)
        data = {}
        i=0
        for chategory in nr_samples_per_month:
            chategory_dict = {'labels':[],'X':[],'Y':[],'color':[]}
            for index, month in MONTHS:
                if not (self.year == str(date.today().year) and index > date.today().month):
                    average = chategory['results'][month]
                    if not average: average=0   
                    chategory_dict['Y'].append(average)
                    chategory_dict['X'].append(index)
                    chategory_dict['labels'].append(month)
            data[chategory['name']] = {'data':chategory_dict, 'color':COLORS[i]}
            i+=1
        print('lhjglgkjhgkj')
        print(data)
        print('lhjglgkjhgkj1111')
        return data

    

