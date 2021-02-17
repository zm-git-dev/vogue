#!/usr/bin/env python

from vogue.constants.constants import MONTHS, MIP_DNA_PICARD


def mip_dna_picard_time_plot(adapter, year: int) -> dict:
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
            'mip-dna': 1,
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
            'mip-dna': 1
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
    for data in MIP_DNA_PICARD.values():
        for key in data:
            final_data[key] = []

    for sample in aggregate_result:
        sample_id = sample['_id']
        mip_dna_analysis = sample.get('mip-dna')
        if mip_dna_analysis:
            multiqc_picard_insertSize = mip_dna_analysis.get(
                'multiqc_picard_insertSize')
            multiqc_picard_HsMetrics = mip_dna_analysis.get(
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


def mip_dna_picard_plot(adapter, year: int) -> dict:
    """Prepares data for the MIP picard plot."""

    all_samples = adapter.bioinfo_samples_collection.find()
    final_data = []

    for sample in all_samples:
        sample_id = sample['_id']
        mip_dna_analysis = sample.get('mip-dna')
        if mip_dna_analysis:
            multiqc_picard_insertSize = mip_dna_analysis.get(
                'multiqc_picard_insertSize')
            multiqc_picard_HsMetrics = mip_dna_analysis.get(
                'multiqc_picard_HsMetrics')
            merged = multiqc_picard_insertSize.copy()
            merged.update(multiqc_picard_HsMetrics)
            merged['_id'] = sample_id
            final_data.append(merged)

    plot_data = {'final_data': final_data, 'labels': [m[1] for m in MONTHS]}

    return (plot_data)
