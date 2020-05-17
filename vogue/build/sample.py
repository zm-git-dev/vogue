from genologics.entities import Sample
from genologics.lims import Lims
from datetime import datetime as dt

from vogue.parse.build.sample import *


def build_sample(sample: Sample, lims: Lims, adapter)-> dict:
    """Parse lims sample"""
    application_tag = sample.udf.get('Sequencing Analysis')
    category = adapter.get_category(application_tag) 
    
    mongo_sample = {'_id' : sample.id}
    mongo_sample['family'] = sample.udf.get('Family')
    mongo_sample['strain'] = sample.udf.get('Strain')
    mongo_sample['source'] = sample.udf.get('Source')
    mongo_sample['customer'] = sample.udf.get('customer')
    mongo_sample['priority'] = sample.udf.get('priority')
    mongo_sample['initial_qc'] = sample.udf.get('Passed Initial QC')
    mongo_sample['library_qc'] = sample.udf.get('Passed Library QC')
    mongo_sample['sequencing_qc'] = sample.udf.get('Passed Sequencing QC')
    mongo_sample['application_tag'] = application_tag
    mongo_sample['category'] = category
    sequenced_at = sample.udf.get('Sequencing Finished')
    received_at = sample.udf.get('Received at')
    prepared_at = sample.udf.get('Library Prep Finished')
    delivered_at = sample.udf.get('Delivered at')
    if sequenced_at:
        mongo_sample['sequenced_date'] = dt(sequenced_at.year, sequenced_at.month, sequenced_at.day)
    if received_at:
        mongo_sample['received_date'] = dt(received_at.year, received_at.month, received_at.day)
    if prepared_at:
        mongo_sample['prepared_date'] = dt(prepared_at.year, prepared_at.month, prepared_at.day)
    if delivered_at:
        mongo_sample['delivery_date'] = dt(delivered_at.year, delivered_at.month, delivered_at.day)
    mongo_sample['sequenced_to_delivered'] = get_number_of_days(sequenced_at, delivered_at)
    mongo_sample['prepped_to_sequenced'] = get_number_of_days(prepared_at, sequenced_at)
    mongo_sample['received_to_prepped'] = get_number_of_days(received_at, prepared_at)
    mongo_sample['received_to_delivered'] = get_number_of_days(received_at, delivered_at)

    conc_and_amount = get_final_conc_and_amount_dna(application_tag, sample.id, lims)
    mongo_sample['amount'] = conc_and_amount.get('amount')
    mongo_sample['amount-concentration'] = conc_and_amount.get('concentration')

    concentration_and_nr_defrosts = get_concentration_and_nr_defrosts(application_tag, sample.id, lims)
    mongo_sample['nr_defrosts'] = concentration_and_nr_defrosts.get('nr_defrosts')
    mongo_sample['nr_defrosts-concentration'] = concentration_and_nr_defrosts.get('concentration')
    mongo_sample['lotnr'] = concentration_and_nr_defrosts.get('lotnr')

    mongo_sample['microbial_library_concentration'] = get_microbial_library_concentration(application_tag, sample.id, lims)
    
    mongo_sample['library_size_pre_hyb'] = get_library_size(application_tag, sample.id, lims, 
                                                            'TWIST', 'library_size_pre_hyb')
    mongo_sample['library_size_post_hyb'] = get_library_size(application_tag, sample.id, lims, 
                                                            'TWIST', 'library_size_post_hyb')
    if not mongo_sample['library_size_post_hyb']:
        if not received_at or received_at < dt(2019, 1, 1):
            mongo_sample['library_size_pre_hyb'] = get_library_size(application_tag, sample.id, lims, 
                                                                'SureSelect', 'library_size_pre_hyb')
            mongo_sample['library_size_post_hyb'] = get_library_size(application_tag, sample.id, lims, 
                                                                'SureSelect', 'library_size_post_hyb')

    for key in list(mongo_sample.keys()):
        if mongo_sample[key] is None:
            mongo_sample.pop(key)

    return mongo_sample
