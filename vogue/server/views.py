#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app

from vogue.constants.constants import *
from vogue.server.utils import *
from vogue import __version__

app = current_app
blueprint = Blueprint('server', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    year = request.form.get('year', str(THIS_YEAR))

    if request.form.get('page') == 'turn_around_times':
        return redirect(url_for('server.turn_around_times', year=year))
    if request.form.get('page') == 'samples':
        return redirect(url_for('server.common_samples', year=year))
    if request.form.get('page') == 'microbial':
        return redirect(url_for('server.microbial', year=year))
    if request.form.get('page') == 'wgs':
        return redirect(url_for('server.wgs', year=year))
    if request.form.get('page') == 'lucigen':
        return redirect(url_for('server.lucigen', year=year))
    if request.form.get('page') == 'target_enrichment':
        return redirect(url_for('server.target_enrichment', year=year))
    if request.form.get('page') == 'runs':
        return redirect(url_for('server.runs', year=year))
    if request.form.get('page') == 'mip_picard_time':
        return redirect(url_for('server.mip_picard_time', year=year))
    if request.form.get('page') == 'mip_picard':
        return redirect(url_for('server.mip_picard', year=year))
    if request.form.get('page') == 'strain_st':
        return redirect(url_for('server.microsalt_strain_st', year=year))
    if request.form.get('page') == 'microsalt_qc_time':
        return redirect(url_for('server.microsalt_qc_time', year=year))
    if request.form.get('page') == 'microsalt_untyped':
        return redirect(url_for('server.microsalt_untyped', year=year))
    if request.form.get('page') == 'microsalt_st_time':
        return redirect(url_for('server.microsalt_st_time', year=year))
    if request.form.get('page') == 'genotype_plate':
        return redirect(url_for('server.genotype_plate'))
    if request.form.get('page') == 'reagent_labels':
        index_category_url = request.form.get('index_category').replace(
            ' ', '_')
        return redirect(
            url_for('server.reagent_labels',
                    index_category_url=index_category_url))
    if request.form.get('page') == 'reagent_label':
        name, category = request.form.get('reagent_label').split(',')
        return redirect(
            url_for('server.reagent_label',
                    reagent_label=name.replace(' ', ''),
                    index_category=category))

    month = int(request.form.get('month', 0))
    sample_series, cathegories = home_samples(app.adapter, int(year), month)
    customers = home_customers(app.adapter, int(year), month)
    return render_template('index.html',
                           version=__version__,
                           sample_series=sample_series,
                           reagent_label=reagent_label,
                           cathegories=cathegories,
                           customers=customers,
                           page_id='index',
                           year_of_interest=year,
                           month_of_interest=month,
                           months=MONTHS,
                           month_name=MONTHS[month - 1][1] if month else '',
                           years=YEARS)


@blueprint.route('/common/turn_around_times/<year>')
def turn_around_times(year):

    y_vals = [
        'received_to_delivered', 'received_to_prepped', 'prepped_to_sequenced',
        'sequenced_to_delivered'
    ]
    results_grouped_by_prio = {}
    results_grouped_by_cat = {}
    for y_val in y_vals:
        results_grouped_by_prio[y_val] = value_per_month(
            app.adapter, year, y_val, "priority")
        results_grouped_by_cat[y_val] = value_per_month(
            app.adapter, year, y_val, "category")

    return render_template('turn_around_times.html',
                           header='Turnaround Times',
                           page_id='turn_around_times',
                           data_prio=results_grouped_by_prio,
                           data_cat=results_grouped_by_cat,
                           months=[m[1] for m in MONTHS],
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/common/samples/<year>')
def common_samples(year):
    data_cat = value_per_month(app.adapter, year, 'count', 'category')
    data_prio = value_per_month(app.adapter, year, 'count', 'priority')
    return render_template('samples.html',
                           header='Samples',
                           page_id='samples',
                           data_prio=data_prio,
                           data_cat=data_cat,
                           months=[m[1] for m in MONTHS],
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/prepps/microbial/<year>')
def microbial(year):
    data = value_per_month(app.adapter, year,
                           'microbial_library_concentration', "strain")

    return render_template('microbial.html',
                           header='Microbial Samples',
                           page_id='microbial',
                           data=data,
                           months=[m[1] for m in MONTHS],
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/prepps/target_enrichment/<year>')
def target_enrichment(year):
    library_size_post_hyb = value_per_month(app.adapter, year,
                                            'library_size_post_hyb', "source")
    library_size_pre_hyb = value_per_month(app.adapter, year,
                                           'library_size_pre_hyb', "source")
    y_axis_label = 'Average Library Size'

    return render_template('target_enrichment.html',
                           header='Target Enrichment (exom/panels)',
                           page_id='target_enrichment',
                           data_pre_hyb=library_size_pre_hyb,
                           data_post_hyb=library_size_post_hyb,
                           months=[m[1] for m in MONTHS],
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/prepps/wgs/<year>')
def wgs(year):
    concentration_time = value_per_month(app.adapter, year,
                                         'nr_defrosts-concentration')
    concentration_defrosts = find_concentration_defrosts(adapter=app.adapter,
                                                         year=year)

    return render_template('wgs.html',
                           header='WGS illumina PCR-free',
                           page_id='wgs',
                           concentration_defrosts=concentration_defrosts,
                           concentration_time=concentration_time,
                           months=[m[1] for m in MONTHS],
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/prepps/lucigen/<year>')
def lucigen(year):
    amount_concentration_time = value_per_month(app.adapter, year,
                                                'amount-concentration')
    concentration_amount = find_concentration_amount(adapter=app.adapter,
                                                     year=year)

    return render_template('lucigen.html',
                           header='Lucigen PCR-free',
                           page_id='lucigen',
                           amount_concentration_time=amount_concentration_time,
                           months=[m[1] for m in MONTHS],
                           amount=concentration_amount,
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/sequencing/runs/<year>', methods=['GET', 'POST'])
def runs(year):
    selcted_metric = request.form.get('metric', '% Bases >=Q30')
    aggregate_result = instrument_info(app.adapter, year, selcted_metric)

    return render_template('runs.html',
                           header='Sequencing Instruments',
                           page_id='runs',
                           metric=selcted_metric,
                           metrices=LANE_UDFS,
                           results=aggregate_result,
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/Bioinfo/Rare_Disease/picard_time/<year>',
                 methods=['GET', 'POST'])
def mip_picard_time(year):
    mip_results = mip_picard_time_plot(app.adapter, year)
    selected_group, selcted_metric = request.form.get(
        'picard_metric', 'PICARD_INSERT_SIZE MEAN_INSERT_SIZE').split()
    return render_template('mip_picard_time.html',
                           selected_group=selected_group,
                           selcted_metric=selcted_metric,
                           mip_results=mip_results,
                           MIP_PICARD=MIP_PICARD,
                           help_urls=BIOINFO_HELP_URLS,
                           months=[m[1] for m in MONTHS],
                           header='MIP',
                           page_id='mip_picard_time',
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/Bioinfo/Rare_Disease/picard/<year>',
                 methods=['GET', 'POST'])
def mip_picard(year):
    mip_results = mip_picard_plot(app.adapter, year)
    Y_group, Y_axis = request.form.get(
        'Y_axis', 'PICARD_INSERT_SIZE MEAN_INSERT_SIZE').split()
    X_group, X_axis = request.form.get(
        'X_axis', 'PICARD_INSERT_SIZE MEAN_INSERT_SIZE').split()
    return render_template('mip_picard.html',
                           Y_axis=Y_axis,
                           X_axis=X_axis,
                           groups=list(set([Y_group, X_group])),
                           mip_results=mip_results,
                           MIP_PICARD=MIP_PICARD,
                           help_urls=BIOINFO_HELP_URLS,
                           header='MIP',
                           page_id='mip_picard',
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/Bioinfo/Cancer/<year>')
def balsamic(year):

    return render_template('balsamic.html',
                           header='Balsamic',
                           page_id='balsamic',
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/Bioinfo/Microbial/strain_st/<year>',
                 methods=['GET', 'POST'])
def microsalt_strain_st(year):
    strain = request.form.get('strain', '')
    results = microsalt_get_strain_st(app.adapter, year)

    return render_template('microsalt_strain_st.html',
                           data=results.get(strain, {}),
                           strain=strain,
                           categories=results.keys(),
                           header='Microsalt',
                           page_id='strain_st',
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@blueprint.route('/Bioinfo/Microbial/qc_time/<year>', methods=['GET', 'POST'])
def microsalt_qc_time(year):
    metric_path = request.form.get('qc_metric',
                                   'picard_markduplicate.insert_size')
    results = microsalt_get_qc_time(app.adapter, year, metric_path)

    return render_template('microsalt_qc_time.html',
                           results=results['data'],
                           categories=results['labels'],
                           mean=results['mean'],
                           selected_group=metric_path.split('.')[0],
                           selected_metric=metric_path.split('.')[1],
                           header='Microsalt',
                           page_id='microsalt_qc_time',
                           version=__version__,
                           year_of_interest=year,
                           MICROSALT=MICROSALT,
                           years=YEARS)


@blueprint.route('/Bioinfo/Microbial/untyped/<year>', methods=['GET', 'POST'])
def microsalt_untyped(year):
    results = microsalt_get_untyped(app.adapter, year)

    return render_template('microsalt_untyped.html',
                           results=results['data'],
                           categories=results['labels'],
                           header='Microsalt',
                           page_id='microsalt_untyped',
                           version=__version__,
                           year_of_interest=year,
                           MICROSALT=MICROSALT,
                           years=YEARS)


@blueprint.route('/Bioinfo/Microbial/st_time/<year>', methods=['GET', 'POST'])
def microsalt_st_time(year):
    strain = request.form.get('strain', 'E.coli')
    results_all = microsalt_get_st_time(app.adapter, year)
    strain_results = results_all['data'].get(strain, {})

    return render_template('microsalt_st_time.html',
                           results=strain_results,
                           results_sorted_keys=sorted(strain_results.keys()),
                           strain=strain,
                           strains=results_all['data'].keys(),
                           categories=results_all['labels'],
                           header='Microsalt',
                           page_id='microsalt_st_time',
                           version=__version__,
                           year_of_interest=year,
                           MICROSALT=MICROSALT,
                           years=YEARS)


@blueprint.route('/Bioinfo/Genotype/plate', methods=['GET', 'POST'])
def genotype_plate():

    plate_id = request.form.get('plate_id')
    plot_data = get_genotype_plate(app.adapter, plate_id=plate_id)
    plot_data['plates'].sort()
    return render_template('genotype_plate.html',
                           plate_data=plot_data['data'],
                           x_labels=plot_data['x_labels'],
                           y_labels=plot_data['y_labels'],
                           year_of_interest=str(THIS_YEAR),
                           header='Genotype',
                           page_id='genotype_plate',
                           version=__version__,
                           plate_id=plot_data['plate_id'],
                           plates=plot_data['plates'])


@blueprint.route('/reagent_labels/<index_category_url>',
                 methods=['GET', 'POST'])
def reagent_labels(index_category_url):
    index_category = index_category_url.replace('_', ' ')
    flowcell_performance_treshold = 0.3
    aggregate_result = reagent_category_data(app.adapter, index_category,
                                             flowcell_performance_treshold)
    return render_template(
        'reagent_labels.html',
        flowcell_performance_treshold=flowcell_performance_treshold,
        header='Overall performance per index',
        page_id='reagent_labels',
        nr_indexes=len(aggregate_result),
        index_category=index_category,
        index_categories=app.adapter.get_reagent_label_categories(),
        year_of_interest=THIS_YEAR,
        results=aggregate_result,
        version=__version__)


@blueprint.route('/reagent_label/<index_category>/<reagent_label>',
                 methods=['GET', 'POST'])
def reagent_label(index_category, reagent_label):
    flowcell_performance_treshold = 0.3
    aggregate_result = reagent_label_data(app.adapter, reagent_label,
                                          flowcell_performance_treshold)
    index_categories = list(
        app.adapter.get_all_reagent_label_names_grouped_by_category())
    return render_template(
        'reagent_label.html',
        flowcell_performance_treshold=flowcell_performance_treshold,
        header='Normalized index performance per flowcell',
        index_category=index_category.replace('_', ' '),
        page_id='reagent_label',
        year_of_interest=THIS_YEAR,
        reagent_label=reagent_label,
        index_categories=index_categories,
        results=aggregate_result,
        version=__version__)
