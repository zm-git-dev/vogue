#!/usr/bin/env python

from mongo_adapter import get_client
from datetime import datetime as dt
import numpy as np
from vogue.constants.constants import (MONTHS, TEST_SAMPLES, MIP_PICARD,
                                       LANE_UDFS)
from statistics import mean


def home_samples(adapter, year, month):
    match = {'year': {'$eq': year}}
    if month:
        match['month'] = {'$eq': month}
    pipe = [{
        '$match': {
            'received_date': {
                '$exists': 'True'
            }
        }
    }, {
        '$project': {
            'month': {
                '$month': '$received_date'
            },
            'year': {
                '$year': '$received_date'
            },
            'category': 1,
            'priority': 1
        }
    }, {
        '$match': match
    }, {
        '$group': {
            '_id': {
                'category': '$category',
                'priority': '$priority'
            },
            'count': {
                '$sum': 1
            }
        }
    }]
    aggregate_result = adapter.samples_aggregate(pipe)
    samples = {}
    samples_output = {}
    cathegories = []
    for result in aggregate_result:
        cat = result['_id'].get('category', 'missing')
        cathegories.append(cat)
        prio = result['_id'].get('priority', 'missing')
        count = result.get('count', 0)
        if prio not in samples:
            samples[prio] = {cat: count}
            samples_output[prio] = []
        else:
            samples[prio][cat] = count

    cathegories = list(set(cathegories))
    for prio, data in samples.items():
        for cat in cathegories:
            samples_output[prio].append(data.get(cat, 0))
    return samples_output, cathegories


def home_customers(adapter, year, month):
    match = {'year': {'$eq': year}}
    if month:
        match['month'] = {'$eq': month}
    pipe = [{
        '$match': {
            'received_date': {
                '$exists': 'True'
            }
        }
    }, {
        '$project': {
            'month': {
                '$month': '$received_date'
            },
            'year': {
                '$year': '$received_date'
            },
            'customer': 1
        }
    }, {
        '$match': match
    }, {
        '$group': {
            '_id': {
                'customer': '$customer'
            },
            'count': {
                '$sum': 1
            }
        }
    }]
    aggregate_result = adapter.samples_aggregate(pipe)
    customers = {}
    for cust in aggregate_result:
        customer = cust['_id'].get('customer') if cust['_id'].get(
            'customer') else 'missing'
        customers[customer] = cust['count']
    return customers


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

    match = {
        '$match': {
            'received_date': {
                '$exists': True
            },
            '_id': {
                '$nin': TEST_SAMPLES
            }
        }
    }
    project = {
        '$project': {
            'month': {
                '$month': '$received_date'
            },
            'year': {
                '$year': '$received_date'
            }
        }
    }
    match_year = {'$match': {'year': {'$eq': year}}}
    group = {'$group': {'_id': {'month': '$month'}}}
    sort = {'$sort': {'_id.month': 1}}

    if group_key:  # grouping by group_key
        match['$match'][group_key] = {'$exists': True}
        project['$project'][group_key] = 1
        group['$group']['_id'][group_key] = '$' + group_key
        sort['$sort']['_id.' + group_key] = 1

    if y_val == 'count':
        # count nr samples per month:
        group['$group'][y_val] = {'$sum': 1}
    else:
        # get average of y_val:
        match['$match'][y_val] = {'$exists': True}
        project['$project'][y_val] = 1
        group['$group'][y_val] = {'$push': '$' + y_val}

    return [match, project, match_year, group, sort]


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
            group_name = group['_id'][group_key]
        else:
            group_name = 'all_samples'
        month = group['_id']['month']
        if y_val == 'count':
            value = group[y_val]
        else:
            value = np.mean([float(val) for val in group[y_val]])

        if group_name not in plot_data:
            plot_data[group_name] = {'data': [None] * 12}
        plot_data[group_name]['data'][month - 1] = value
    return plot_data


def value_per_month(adapter, year: str, y_val: str, group_key: str = None):
    """Wraper function that will build a pipe, aggregate results from database and 
    prepare the data for the plot."""

    pipe = pipe_value_per_month(int(year), y_val, group_key)
    aggregate_result = adapter.samples_aggregate(pipe)
    return reformat_aggregate_results(list(aggregate_result), y_val, group_key)


def find_concentration_amount(adapter, year: int = None) -> dict:
    """Prepares data for a scatter plot showning Concentration agains Amount."""

    amount = {'data': []}
    pipe = [{
        '$match': {
            'received_to_delivered': {
                '$exists': True
            },
            'amount': {
                '$exists': True
            },
            'amount-concentration': {
                '$exists': True
            }
        }
    }, {
        '$project': {
            'year': {
                '$year': '$received_date'
            },
            'amount': 1,
            'amount-concentration': 1
        }
    }, {
        '$match': {
            'year': {
                '$eq': int(year)
            }
        }
    }]

    aggregate_result = adapter.samples_aggregate(pipe)
    for sample in aggregate_result:
        if sample['amount'] > 200:
            sample['amount'] = 200
        amount['data'].append({
            'x': sample['amount'],
            'y': round(sample['amount-concentration'], 2),
            'name': sample['_id']
        })
    return amount


def find_concentration_defrosts(adapter, year: int) -> dict:
    """Prepares data for a plot showning Number of defrosts against Concentration"""

    nr_defrosts = list(adapter.sample_collection.distinct('nr_defrosts'))
    defrosts = {
        'axis': {
            'x': 'Number of Defrosts',
            'y': 'Concentration (nM)'
        },
        'data': {},
        'title': 'wgs illumina PCR-free',
        'labels': nr_defrosts.sort()
    }

    pipe = [{
        '$match': {
            'received_to_delivered': {
                '$exists': True
            },
            'nr_defrosts-concentration': {
                '$exists': True
            },
            'nr_defrosts': {
                '$exists': True
            },
            'lotnr': {
                '$exists': True
            }
        }
    }, {
        '$project': {
            'year': {
                '$year': '$received_date'
            },
            'nr_defrosts-concentration': 1,
            'nr_defrosts': 1,
            'lotnr': 1
        }
    }, {
        '$match': {
            'year': {
                '$eq': int(year)
            }
        }
    }, {
        '$group': {
            '_id': {
                'nr_defrosts': '$nr_defrosts',
                'lotnr': '$lotnr'
            },
            'count': {
                '$sum': 1
            },
            'values': {
                '$push': '$nr_defrosts-concentration'
            }
        }
    }, {
        '$sort': {
            '_id.nr_defrosts': 1
        }
    }]
    aggregate_result = adapter.samples_aggregate(pipe)

    for result in aggregate_result:
        group = result['_id']['lotnr']
        if group not in defrosts['data']:
            defrosts['data'][group] = {
                'median': [],
                'quartile': [],
                'nr_samples': []
            }
        nr = result['_id']['nr_defrosts']
        values = np.array(result['values'])
        defrosts['data'][group]['median'].append(
            [nr, round(np.percentile(values, 50), 2)])
        defrosts['data'][group]['quartile'].append([
            nr,
            round(np.percentile(values, 25), 2),
            round(np.percentile(values, 75), 2)
        ])
        defrosts['data'][group]['nr_samples'].append([nr, result['count']])

    return defrosts


def instrument_info(adapter, year: int, metric: str) -> dict:
    """Prepares data for a plot Q30 values for diferent runs over time"""
    instruments = {
        'axis': {
            'y': 'Average Q30'
        },
        'data': {p: {}
                 for p in LANE_UDFS},
        'title': 'Q30'
    }
    pipe = [{
        '$project': {
            'year': {
                '$year': '$date'
            },
            'instrument': 1,
            'date': 1,
            'avg': 1
        }
    }, {
        '$match': {
            'year': {
                '$eq': int(year)
            }
        }
    }, {
        '$group': {
            '_id': {
                'instrument': '$instrument'
            },
            'data': {
                '$push': {
                    metric: '$avg.' + metric,
                    'date': '$date',
                    'run_id': '$_id'
                }
            }
        }
    }]

    aggregate_result = adapter.flowcells_aggregate(pipe)

    for result in aggregate_result:
        group = result['_id']['instrument']
        for plot_name in LANE_UDFS:
            data_tuples = [(d['date'], d['run_id'], d.get(plot_name))
                           for d in result['data']]
            data_sorted = sorted(data_tuples)
            data = []
            for date, run_id, value in data_sorted:
                if value:
                    data.append([date, value, run_id])
            if data:
                instruments['data'][plot_name][group] = {'data': data}

    return instruments


def mip_picard_time_plot(adapter, year: int) -> dict:
    """Prepares data for the MIP picard over time plot."""

    pipe = [{
        '$lookup': {
            'from': 'sample',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'sample_info'
        }
    }, {
        '$unwind': {
            'path': '$sample_info'
        }
    }, {
        '$match': {
            'sample_info.received_date': {
                '$exists': 'True'
            }
        }
    }, {
        '$project': {
            'mip': 1,
            'received_date': '$sample_info.received_date'
        }
    }, {
        '$match': {
            'received_date': {
                '$exists': 'True'
            }
        }
    }, {
        '$project': {
            'month': {
                '$month': '$received_date'
            },
            'year': {
                '$year': '$received_date'
            },
            'mip': 1
        }
    }, {
        '$match': {
            'year': {
                '$eq': int(year)
            }
        }
    }]
    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    final_data = {}
    for data in MIP_PICARD.values():
        for key in data:
            final_data[key] = []

    for sample in aggregate_result:
        sample_id = sample['_id']
        mip_analysis = sample.get('mip')
        if mip_analysis:
            multiqc_picard_insertSize = mip_analysis.get(
                'multiqc_picard_insertSize')
            multiqc_picard_HsMetrics = mip_analysis.get(
                'multiqc_picard_HsMetrics')
            for key, val in multiqc_picard_insertSize.items():
                if key in final_data.keys():
                    final_data[key].append({
                        'name': sample_id,
                        'x': sample['month'],
                        'y': val
                    })
            for key, val in multiqc_picard_HsMetrics.items():
                if key in final_data.keys():
                    final_data[key].append({
                        'name': sample_id,
                        'x': sample['month'],
                        'y': val
                    })

    plot_data = {'data': final_data, 'labels': [m[1] for m in MONTHS]}

    return (plot_data)


def mip_picard_plot(adapter, year: int) -> dict:
    """Prepares data for the MIP picard plot."""

    all_samples = adapter.bioinfo_samples_collection.find()
    final_data = []

    for sample in all_samples:
        sample_id = sample['_id']
        mip_analysis = sample.get('mip')
        if mip_analysis:
            multiqc_picard_insertSize = mip_analysis.get(
                'multiqc_picard_insertSize')
            multiqc_picard_HsMetrics = mip_analysis.get(
                'multiqc_picard_HsMetrics')
            merged = multiqc_picard_insertSize.copy()
            merged.update(multiqc_picard_HsMetrics)
            merged['_id'] = sample_id
            final_data.append(merged)

    plot_data = {'final_data': final_data, 'labels': [m[1] for m in MONTHS]}

    return (plot_data)


def microsalt_get_strain_st(adapter, year: int) -> dict:
    pipe = [{
        '$match': {
            'microsalt': {
                '$exists': 'True'
            }
        }
    }, {
        '$lookup': {
            'from': 'sample',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'sample_info'
        }
    }, {
        '$unwind': {
            'path': '$sample_info'
        }
    }, {
        '$match': {
            'sample_info.received_date': {
                '$exists': 'True'
            }
        }
    }, {
        '$project': {
            'strain': '$sample_info.strain',
            'year': {
                '$year': '$sample_info.received_date'
            },
            'sequence_type': '$microsalt.blast_pubmlst.sequence_type'
        }
    }, {
        '$match': {
            'year': {
                '$eq': int(year)
            }
        }
    }, {
        '$group': {
            '_id': {
                'strain': '$strain',
                'sequence_type': '$sequence_type'
            },
            'number': {
                '$sum': 1
            }
        }
    }, {
        '$match': {
            'number': {
                '$exists': 'True'
            },
            '_id.sequence_type': {
                '$exists': 'True'
            }
        }
    }, {
        '$group': {
            '_id': '$_id.strain',
            'number': {
                '$push': '$number'
            },
            'sequence_type': {
                '$push': '$_id.sequence_type'
            }
        }
    }]

    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    plot_data = {}
    for strain_results in aggregate_result:
        strain = strain_results['_id']
        st = strain_results['sequence_type']
        counts = strain_results['number']
        data = [(st[i], c) for i, c in enumerate(counts)]
        plot_data[strain] = sorted(data)
    return plot_data


def microsalt_get_qc_time(adapter, year: int, metric_path: str) -> dict:
    """Build aggregation pipeline to get information for microsalt qc data over time.
    """
    metric = metric_path.split('.')[1]
    pipe = [{
        '$match': {
            'microsalt': {
                '$exists': 'True'
            }
        }
    }, {
        '$lookup': {
            'from': 'sample',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'sample_info'
        }
    }, {
        '$unwind': {
            'path': '$sample_info'
        }
    }, {
        '$match': {
            'sample_info.received_date': {
                '$exists': 'True'
            }
        }
    }, {
        '$project': {
            'month': {
                '$month': '$sample_info.received_date'
            },
            'year': {
                '$year': '$sample_info.received_date'
            },
            metric: '$microsalt.' + metric_path
        }
    }, {
        '$match': {
            'year': {
                '$eq': int(year)
            }
        }
    }, {
        '$group': {
            '_id': {
                'month': '$month'
            },
            metric: {
                '$push': '$' + metric
            }
        }
    }]

    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    intermediate = {
        result['_id']['month']: result[metric]
        for result in aggregate_result
    }
    box_plots = []
    labels = []
    means = []
    for m in MONTHS:
        values = intermediate.get(m[0], [])
        if values:
            minimum = round(min(values), 2)
            low = round(np.percentile(values, 25), 2)
            med = round(np.median(values), 2)
            high = round(np.percentile(values, 75), 2)
            maximum = round(max(values), 2)
            means.append(np.mean(values))
            box_plots.append([minimum, low, med, high, maximum])
        else:
            box_plots.append([])
        labels.append(m[1])

    plot_data = {
        'data': box_plots,
        'labels': labels,
        'mean': round(np.mean(means), 2)
    }

    return plot_data


def microsalt_get_untyped(adapter, year: int) -> dict:
    """Build aggregation pipeline to get information for microsalt qc data over time.
    """
    pipe = [{
        '$match': {
            'microsalt': {
                '$exists': 'True'
            }
        }
    }, {
        '$lookup': {
            'from': 'sample',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'sample_info'
        }
    }, {
        '$unwind': {
            'path': '$sample_info'
        }
    }, {
        '$match': {
            'sample_info.received_date': {
                '$exists': 'True'
            }
        }
    }, {
        '$project': {
            'month': {
                '$month': '$sample_info.received_date'
            },
            'year': {
                '$year': '$sample_info.received_date'
            },
            'ST': '$microsalt.blast_pubmlst.sequence_type'
        }
    }, {
        '$match': {
            'year': {
                '$eq': int(year)
            }
        }
    }, {
        '$group': {
            '_id': {
                'month': '$month'
            },
            'ST': {
                '$push': '$ST'
            }
        }
    }]

    intermediate = {}
    aggregate_result = adapter.bioinfo_samples_aggregate(pipe)
    for result in aggregate_result:
        untyped = 0
        typed = 0
        for st in result['ST']:
            try:
                st = int(st)
                if -9 < st < -1:
                    untyped += 1
                else:
                    typed += 1
            except:
                pass
        if typed + untyped:
            fraction = untyped / (typed + untyped)
        else:
            fraction = None
        intermediate[result['_id']['month']] = fraction

    data = []
    labels = []
    for m in MONTHS:
        value = intermediate.get(m[0], None)
        data.append(value)
        labels.append(m[1])

    plot_data = {'data': data, 'labels': labels}
    return plot_data


def microsalt_get_st_time(adapter, year: int) -> dict:
    pipe = [{
        '$match': {
            'microsalt': {
                '$exists': 'True'
            }
        }
    }, {
        '$lookup': {
            'from': 'sample',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'sample_info'
        }
    }, {
        '$unwind': {
            'path': '$sample_info'
        }
    }, {
        '$match': {
            'sample_info.received_date': {
                '$exists': 'True'
            }
        }
    }, {
        '$project': {
            'month': {
                '$month': '$sample_info.received_date'
            },
            'strain': '$sample_info.strain',
            'year': {
                '$year': '$sample_info.received_date'
            },
            'sequence_type': '$microsalt.blast_pubmlst.sequence_type'
        }
    }, {
        '$match': {
            'year': {
                '$eq': int(year)
            },
            'sequence_type': {
                '$exists': 'True'
            },
            'strain': {
                '$exists': 'True'
            }
        }
    }, {
        '$group': {
            '_id': {
                'month': '$month',
                'strain': '$strain',
                'sequence_type': '$sequence_type'
            },
            'number': {
                '$sum': 1
            }
        }
    }]
    final_results = {}
    aggregate_result = list(adapter.bioinfo_samples_aggregate(pipe))
    for result in aggregate_result:
        st = result['_id']['sequence_type']
        strain = result['_id']['strain']
        if final_results.get(strain):
            final_results[strain][st] = [None] * 12
        else:
            final_results[strain] = {st: [None] * 12}
    for result in aggregate_result:
        count = result.get('number')
        if count:
            month = result['_id']['month']
            st = result['_id']['sequence_type']
            strain = result['_id']['strain']
            final_results[strain][st][month - 1] = count

    return {'data': final_results, 'labels': [m[1] for m in MONTHS]}


def get_genotype_plate(adapter, plate_id: str) -> dict:
    plates_pipe = [{
        '$match': {
            'plate': {
                '$exists': 'True'
            },
            'snps.comp': {
                '$exists': 'True'
            }
        }
    }, {
        '$group': {
            '_id': {
                'plate': '$plate'
            }
        }
    }]
    aggregate_result = list(adapter.genotype_analysis_aggregate(plates_pipe))
    plates = [plate['_id']['plate'] for plate in aggregate_result]

    plate_id = plates[0] if not plate_id else plate_id

    samples_pipe = [{
        '$match': {
            'plate': plate_id,
            'snps.comp': {
                '$exists': 'True'
            }
        }
    }]

    samples = list(adapter.genotype_analysis_aggregate(samples_pipe))
    data = []
    x_labels = list(samples[0]['snps']['comp'].keys())
    y_labels = []
    x_labels.sort()
    for row, sample in enumerate(samples):
        comp = sample['snps'].get('comp')
        genotype = sample['snps'].get('genotype')
        sequence = sample['snps'].get('sequence')
        y_labels.append(sample['_id'])
        for col, key in enumerate(x_labels):
            internal = ''.join(genotype[key])
            external = ''.join(sequence[key])
            data.append((col, row, int(comp[key]), f'{internal} : {external}'))

    return {
        'data': data,
        'x_labels': x_labels,
        'y_labels': y_labels,
        'plates': plates,
        'plate_id': plate_id
    }
