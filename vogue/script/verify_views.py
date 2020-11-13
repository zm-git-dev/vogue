from genologics.lims import Lims
from genologics.config import BASEURI, USERNAME, PASSWORD
from genologics.entities import Process, Sample
lims = Lims(BASEURI, USERNAME, PASSWORD)
from vogue.constants.lims_constants import MASTER_STEPS_UDFS, INSTRUMENTS, TEST_SAMPLES
from statistics import mean
import numpy as np
from vogue.server import create_app
import datetime as dt
app = create_app()

#getting all samples recieved in 2017
recieved_steps = lims.get_processes(
    type=MASTER_STEPS_UDFS['received']['steps'])
samples_2017 = {}
for step in recieved_steps:
    date = step.udf.get('date arrived at clinical genomics')
    if not date:
        date = step.date_run
        date = dt.datetime.strptime(date, '%Y-%m-%d').date()
    if date and date.year == 2017:
        for art in step.all_inputs():
            sample = art.samples[0]
            if sample.id in TEST_SAMPLES:
                continue
            if sample not in samples_2017:
                samples_2017[sample] = date
            elif samples_2017[sample] > date:
                samples_2017[sample] = date

#getting all samples recieved in 2018
recieved_steps = lims.get_processes(
    type=MASTER_STEPS_UDFS['received']['steps'])
samples_2018 = {}
for step in recieved_steps:
    date = step.udf.get('date arrived at clinical genomics')
    if not date:
        date = step.date_run
        date = dt.datetime.strptime(date, '%Y-%m-%d').date()
    if date and date.year == 2018:
        for art in step.all_inputs():
            sample = art.samples[0]
            if sample.id in TEST_SAMPLES:
                continue
            if sample not in samples_2018:
                samples_2018[sample] = date
            elif samples_2018[sample] > date:
                samples_2018[sample] = date

#getting all samples recieved in 2019
recieved_steps = lims.get_processes(
    type=MASTER_STEPS_UDFS['received']['steps'])
samples_2019 = {}
for step in recieved_steps:
    date = step.udf.get('date arrived at clinical genomics')
    if not date:
        date = step.date_run
        date = dt.datetime.strptime(date, '%Y-%m-%d').date()
    if date and date.year == 2019:
        for art in step.all_inputs():
            sample = art.samples[0]
            if sample.id in TEST_SAMPLES:
                continue
            if sample not in samples_2019:
                samples_2019[sample] = date
            elif samples_2019[sample] > date:
                samples_2019[sample] = date

samples_2019_grouped_priority = {
    'express': [],
    'priority': [],
    'standard': [],
    'research': []
}
for sample in samples_2019:
    priority = sample.udf.get('priority')
    samples_2019_grouped_priority[priority].append(sample)

# Customers in 2017
samples_grouped_by_cust = {}
for sample in samples_2017:
    cust = sample.udf.get('customer')
    if cust not in samples_grouped_by_cust:
        samples_grouped_by_cust[cust] = [sample]
    else:
        samples_grouped_by_cust[cust].append(sample)

for key, val in samples_grouped_by_cust.items():
    print key
    print len(val)

## Concentration - defrosts for lot nr 20139912
processes = lims.get_processes(
    type=MASTER_STEPS_UDFS['concentration_and_nr_defrosts']['lot_nr_step'],
    udf={
        MASTER_STEPS_UDFS['concentration_and_nr_defrosts']['lot_nr_udf']:
        '20139912'
    })
conc_defrosts = {}
for process in processes:
    outarts = process.all_outputs()
    values = []
    for art in outarts:
        conc = art.udf.get('Concentration (nM)')
        if conc:
            values.append(conc)
    conc_defrosts[process.date_run] = round(np.percentile(values, 50), 2)

conc_defrosts_sorted = conc_defrosts.items()
conc_defrosts_sorted.sort()

## Concentration wgs PCR-free over time
concentrations_months = {}
for sample, date in samples_2017.items():
    artifacts = lims.get_artifacts(
        process_type=MASTER_STEPS_UDFS['concentration_and_nr_defrosts']
        ['lot_nr_step'],
        samplelimsid=sample.id)
    if artifacts:
        art = artifacts[-1]
        lotnr = art.parent_process.udf.get(
            MASTER_STEPS_UDFS['concentration_and_nr_defrosts']['lot_nr_udf'])
        if lotnr and len(lotnr.split(',')) == 1 and len(lotnr.split(' ')) == 1:
            month = date.month
            conc = art.udf.get('Concentration (nM)')
            if not conc:
                continue
            if month not in concentrations_months:
                concentrations_months[month] = [conc]
            else:
                concentrations_months[month].append(conc)
concentrations_months_sorted = concentrations_months.items()
concentrations_months_sorted.sort()

for month in concentrations_months_sorted:
    print month[0]
    print mean(month[1])

## Concentration lucigen over time
concentrations_months = {}

for sample, date in samples_2017.items():
    # Check only samples with correct apptag
    if sample.udf.get('Sequencing Analysis')[0:6] not in ['WGSLIF', 'WGTLIF']:
        continue

    #get output artifacts from the correct step that are related to the sample
    artifacts = lims.get_artifacts(
        process_type=MASTER_STEPS_UDFS['final_conc_and_amount_dna']
        ['concentration_step'],
        samplelimsid=sample.id)

    #get the input artifacts that holds the concentration udf
    #append the condentration to the correct month
    if artifacts:
        inarts = artifacts[-1].parent_process.all_inputs()
        for art in inarts:

            if art.samples[0].id != sample.id:
                continue
            conc = art.udf.get(MASTER_STEPS_UDFS['final_conc_and_amount_dna']
                               ['concentration_udf'])
            month = date.month
            if not conc:
                continue
            if month not in concentrations_months:
                concentrations_months[month] = [conc]
            else:
                concentrations_months[month].append(conc)

# sort by month
concentrations_months_sorted = concentrations_months.items()
concentrations_months_sorted.sort()

for month in concentrations_months_sorted:
    print month[0]
    print mean(month[1])

## Concentration amount lucigen
concentration_amount = []

for sample in samples_2018:
    if sample.udf.get('Sequencing Analysis')[0:6] not in MASTER_STEPS_UDFS[
            'final_conc_and_amount_dna']['apptags']:
        continue
    artifacts = lims.get_artifacts(
        process_type=MASTER_STEPS_UDFS['final_conc_and_amount_dna']
        ['concentration_step'],
        samplelimsid=sample.id)
    if artifacts:
        inarts = artifacts[-1].parent_process.all_inputs()
        for art in inarts:
            if art.samples[0].id != sample.id:
                continue
            conc = art.udf.get(MASTER_STEPS_UDFS['final_conc_and_amount_dna']
                               ['concentration_udf'])
    artifacts = lims.get_artifacts(
        process_type=MASTER_STEPS_UDFS['final_conc_and_amount_dna']
        ['amount_step'],
        samplelimsid=sample.id)
    if artifacts:
        inarts = artifacts[-1].parent_process.all_inputs()
        for art in inarts:
            if art.samples[0].id != sample.id:
                continue
            amount = art.udf.get(
                MASTER_STEPS_UDFS['final_conc_and_amount_dna']['amount_udf'])
            if amount > 200:
                amount = 200
    concentration_amount.append({
        'name': sample.id,
        'x': amount,
        'y': round(conc, 2)
    })

concentration_amount

## Concentration Microbial over time
mic_tags_ = app.db.get_collection('application_tag').find(
    {'category': {
        '$eq': 'mic'
    }})
mic_tags = []
for doc in mic_tags_:
    mic_tags.append(doc['_id'])

concentrations_months_organism = {}
for sample, date in samples_2018.items():
    # Check only samples with correct apptag
    if sample.udf.get('Sequencing Analysis') not in mic_tags:
        continue
    #get organism
    organism = sample.udf.get('Strain')
    if not organism:
        continue
    if not organism in concentrations_months_organism:
        concentrations_months_organism[organism] = {}
    #get output artifacts from the correct step that are related to the sample
    artifacts = lims.get_artifacts(
        process_type=MASTER_STEPS_UDFS['microbial_library_concentration']
        ['concentration_step'],
        samplelimsid=sample.id)
    #get the input artifacts that holds the concentration udf
    #append the condentration to the correct month
    if artifacts:
        inarts = artifacts[-1].parent_process.all_inputs()
        for art in inarts:
            if art.samples[0].id != sample.id:
                continue
            conc = art.udf.get(
                MASTER_STEPS_UDFS['microbial_library_concentration']
                ['concentration_udf'])
            month = date.month
            if conc is None:
                continue
            if month not in concentrations_months_organism[organism]:
                concentrations_months_organism[organism][month] = [conc]
            else:
                concentrations_months_organism[organism][month].append(conc)

for organism, month_data in concentrations_months_organism.items():
    print('#################################')
    print(organism)
    month_data_sorted = list(month_data.items())
    month_data_sorted.sort()
    # sort by month
    for month in month_data_sorted:
        print(month[0])
        print(mean(month[1]))

## Samples over time Category
apptags_collection = app.db.get_collection('application_tag')
category_samples = {}
for sample, date in samples_2018.items():
    # Check only samples with correct apptag
    tag = sample.udf.get('Sequencing Analysis')
    if not tag:
        continue
    try:
        cat = apptags_collection.find_one(tag).get('category')
    except:
        continue
    month = date.month
    if not cat in category_samples:
        category_samples[cat] = {month: 1}
    elif month not in category_samples[cat]:
        category_samples[cat][month] = 1
    else:
        category_samples[cat][month] += 1

for cat, month_data in category_samples.items():
    print('#################################')
    print(cat)
    month_data_sorted = list(month_data.items())
    month_data_sorted.sort()
    print(month_data_sorted)

## Samples over time Priority
priority_samples = {}
for sample, date in samples_2018.items():
    # Check only samples with correct apptag
    prio = sample.udf.get('priority')
    if not prio:
        continue

    month = date.month
    if not prio in priority_samples:
        priority_samples[prio] = {month: 1}
    elif month not in priority_samples[prio]:
        priority_samples[prio][month] = 1
    else:
        priority_samples[prio][month] += 1

for priority, month_data in priority_samples.items():
    print('#################################')
    print(prio)
    month_data_sorted = list(month_data.items())
    month_data_sorted.sort()
    print(month_data_sorted)

## Runs
instruments = {}
nova_runs = lims.get_processes(type=['AUTOMATED - NovaSeq Run'])
for run in nova_runs:
    run_id = run.udf.get('Run ID')
    if not run_id:
        continue
    date, instrument = run_id.split('_')[0:2]
    if not date:
        continue
    date_ = dt.datetime.strptime(date, '%y%m%d')
    if date_.year != 2019:
        continue
    instrument_name = INSTRUMENTS.get(instrument)
    if instrument_name not in instruments:
        instruments[instrument_name] = []
    lanes = run.all_outputs()
    Q30 = []
    for lane in lanes:
        if not lane.location:
            continue
        name = lane.name
        if not 'Lane' in name.split():
            continue

        q30_r1 = lane.udf.get(MASTER_STEPS_UDFS['sequenced']['q30r1_udf'])
        q30_r2 = lane.udf.get(MASTER_STEPS_UDFS['sequenced']['q30r2_udf'])
        if q30_r1 is not None and q30_r2 is not None:
            Q30.append(q30_r1)
            Q30.append(q30_r2)
    avg = round(np.mean(Q30), 2)
    instruments[instrument_name].append((date, avg, run_id.split('_')[-1]))

## Target Enrichment size bp over time
#Sure select
size_months_source = {}
arts = lims.get_artifacts(
    process_type=MASTER_STEPS_UDFS['library_size_post_hyb']['SureSelect']
    ['size_step'])
for art in arts:
    sample = art.samples[0]
    if not sample in samples_2018:
        continue
    if sample.udf.get('Sequencing Analysis')[0:3] not in MASTER_STEPS_UDFS[
            'library_size_post_hyb']['SureSelect']['apptags']:
        continue
    date = samples_2018[art.samples[0]]
    source = sample.udf.get('Source')
    size = art.udf.get(
        MASTER_STEPS_UDFS['library_size_post_hyb']['SureSelect']['size_udf'])
    if not (source and size):
        continue
    month = date.month
    if not source in size_months_source:
        size_months_source[source] = {month: [size]}
    elif not month in size_months_source[source]:
        size_months_source[source][month] = [size]
    else:
        size_months_source[source][month].append(size)

for source, month_data in size_months_source.items():
    print(source)
    for month, data in month_data.items():
        print(month, round(np.mean(data), 2))

# TWIST
size_months_source = {}
stage_udfs = MASTER_STEPS_UDFS['library_size_pre_hyb']['TWIST'].get(
    'stage_udf')
process_types = MASTER_STEPS_UDFS['library_size_pre_hyb']['TWIST']['size_step']
for samp, date in samples_2019.items():
    artifacts = lims.get_artifacts(samplelimsid=samp.id,
                                   process_type=process_types)
    if not artifacts:
        continue
    art = artifacts[-1]
    size = None
    for inart in art.parent_process.all_inputs():
        stage = inart.workflow_stages[0].id
        if samp in inart.samples and stage in stage_udfs:
            size_udf = stage_udfs[stage]
            size = inart.udf.get(size_udf)
            break
    if size:
        month = date.month
        source = samp.udf.get('Source')
        if not source in size_months_source:
            size_months_source[source] = {month: [(size, samp.id)]}
        elif not month in size_months_source[source]:
            size_months_source[source][month] = [(size, samp.id)]
        else:
            size_months_source[source][month].append((size, samp.id))

for source, month_data in size_months_source.items():
    print(source)
    for month, data in month_data.items():
        sizes = [float(size[0]) for size in data]
        #print(data)
        print(month, round(np.mean(sizes), 2))


##Turnaround Times
def str_to_datetime(date: str) -> dt:
    if date is None:
        return None
    return dt.datetime.strptime(date, '%Y-%m-%d')


def get_prepared_date(sample) -> dt:
    """Get the first date when a sample was prepared in the lab.
    """
    artifacts = lims.get_artifacts(
        samplelimsid=sample.id,
        process_type=MASTER_STEPS_UDFS['prepared']['steps'])
    if not artifacts:
        return None
    artifact = artifacts[-1]
    prepared_date = None
    if artifact:
        prepared_date = str_to_datetime(artifact.parent_process.date_run)
    return prepared_date.date()


def get_number_of_days(first_date: dt, second_date: dt) -> int:
    """Get number of days between different time stamps."""
    days = None
    if first_date and second_date:
        time_span = second_date - first_date
        days = time_span.days
    return days


times = {}
for sample, recieved_date in samples_2018.items():
    prio = sample.udf.get('priority')
    prepp_date = get_prepared_date(sample)
    month = recieved_date.month
    diff = get_number_of_days(recieved_date, prepp_date)
    if not prio in times:
        times[prio] = {month: [diff]}
    elif not month in times[prio]:
        times[prio][month] = [diff]
    else:
        times[prio][month].append(diff)

for prio, month_data in times.items():
    print(prio)
    for month, data in month_data.items():
        non_nones = []
        for v in data:
            if v:
                non_nones.append(v)
        print(month, round(np.mean(non_nones), 2))
