from genologics.entities import Sample
from genologics.lims import Lims
from datetime import datetime as dt

from vogue.parse.build.sample import *


def build_sample(sample: Sample, lims: Lims, adapter) -> dict:
    """Build lims sample"""

    application_tag = sample.udf.get('Sequencing Analysis')
    category = adapter.get_category(application_tag)
    received_at = datetime2date(sample.udf.get('Received at'))
    delivered_at = datetime2date(sample.udf.get('Delivered at'))
    sequenced_at = datetime2date(sample.udf.get('Sequencing Finished'))
    prepared_at = datetime2date(sample.udf.get('Library Prep Finished'))

    mongo_sample = {'_id': sample.id}
    mongo_sample['sequenced_date'] = sequenced_at
    mongo_sample['received_date'] = received_at
    mongo_sample['prepared_date'] = prepared_at
    mongo_sample['delivery_date'] = delivered_at
    mongo_sample['sequenced_to_delivered'] = get_number_of_days(
        sequenced_at, delivered_at)
    mongo_sample['prepped_to_sequenced'] = get_number_of_days(
        prepared_at, sequenced_at)
    mongo_sample['received_to_prepped'] = get_number_of_days(
        received_at, prepared_at)
    mongo_sample['received_to_delivered'] = get_number_of_days(
        received_at, delivered_at)
    mongo_sample['family'] = sample.udf.get('Family')
    mongo_sample['strain'] = sample.udf.get('Strain')
    mongo_sample['source'] = sample.udf.get('Source')
    mongo_sample['customer'] = sample.udf.get('customer')
    mongo_sample['priority'] = sample.udf.get('priority')
    mongo_sample['initial_qc'] = sample.udf.get('Passed Initial QC')
    mongo_sample['library_qc'] = sample.udf.get('Passed Library QC')
    mongo_sample['prep_method'] = sample.udf.get('Prep Method')
    mongo_sample['sequencing_qc'] = sample.udf.get('Passed Sequencing QC')
    mongo_sample['application_tag'] = application_tag
    mongo_sample['category'] = category

    conc_and_amount = get_final_conc_and_amount_dna(application_tag, sample.id,
                                                    lims)
    mongo_sample['amount'] = conc_and_amount.get('amount')
    mongo_sample['amount-concentration'] = conc_and_amount.get('concentration')

    concentration_and_nr_defrosts = get_concentration_and_nr_defrosts(
        application_tag, sample.id, lims)
    mongo_sample['nr_defrosts'] = concentration_and_nr_defrosts.get(
        'nr_defrosts')
    mongo_sample[
        'nr_defrosts-concentration'] = concentration_and_nr_defrosts.get(
            'concentration')
    mongo_sample['lotnr'] = concentration_and_nr_defrosts.get('lotnr')

    mongo_sample[
        'microbial_library_concentration'] = get_microbial_library_concentration(
            application_tag, sample.id, lims)

    mongo_sample['library_size_pre_hyb'] = get_library_size(
        sample_id=sample.id, lims=lims, workflow='TWIST', size_steps=['KAPA Library Preparation TWIST v1'])
    mongo_sample['library_size_post_hyb'] = get_library_size(
        sample_id=sample.id, lims=lims, workflow='TWIST', size_steps=['Bead Purification TWIST v2', 'Bead Purification TWIST v1'])

    for key in list(mongo_sample.keys()):
        if mongo_sample[key] is None:
            mongo_sample.pop(key)

    return mongo_sample
