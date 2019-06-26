#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app

from vogue.constants.constants import YEARS, THIS_YEAR, PICARD_INSERT_SIZE, PICARD_HS_METRIC, MICROSALT
from vogue.server.utils import *


app = current_app
blueprint = Blueprint('server', __name__)

@blueprint.route('/', methods=['GET', 'POST'])
def index():
    year = request.form.get('year')
    if not year:
        year = THIS_YEAR

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

    return render_template(
        'index.html',
        year_of_interest = year)

@blueprint.route('/common/turn_around_times/<year>')
def turn_around_times(year):

    y_vals = ['received_to_delivered', 'received_to_prepped', 'prepped_to_sequenced', 'sequenced_to_delivered']

    results_grouped_by_prio = value_per_month(app.adapter, year, y_vals, "priority")
    results_grouped_by_cat = value_per_month(app.adapter, year, y_vals, "category")
    y_axis_label = 'Days'

    # plot titles
    r2d_c = 'Time from recieved to delivered (grouped by application tag category)'
    r2d_p = 'Time from recieved to delivered (grouped by priority)'
    r2p_c = 'Time from recieved to prepped (grouped by application tag category)'
    r2p_p = 'Time from recieved to prepped (grouped by priority)'
    p2s_c = 'Time from prepped to sequenced (grouped by application tag category)'
    p2s_p = 'Time from prepped to sequenced (grouped by priority)'                            
    s2d_c = 'Time from sequenced to delivered (grouped by application tag category)'
    s2d_p = 'Time from sequenced to delivered (grouped by priority)'

    return render_template('turn_around_times.html',
        header = 'Turnaround Times',
        page_id = 'turn_around_times',
        data_prio = results_grouped_by_prio,
        data_cat = results_grouped_by_cat,
        received_to_delivered_cat = plot_attributes( title = r2d_c , y_axis_label = y_axis_label),
        received_to_delivered_prio = plot_attributes( title = r2d_p , y_axis_label = y_axis_label),
        received_to_prepped_cat = plot_attributes( title = r2p_c , y_axis_label = y_axis_label),
        received_to_prepped_prio = plot_attributes( title = r2p_p , y_axis_label = y_axis_label),
        prepped_to_sequenced_cat = plot_attributes( title = p2s_c , y_axis_label = y_axis_label),
        prepped_to_sequenced_prio = plot_attributes( title = p2s_p , y_axis_label = y_axis_label),
        sequenced_to_delivered_cat = plot_attributes( title = s2d_c , y_axis_label = y_axis_label),
        sequenced_to_delivered_prio = plot_attributes( title = s2d_p , y_axis_label = y_axis_label),
        year_of_interest=year,
        years = YEARS)


@blueprint.route('/common/samples/<year>')
def common_samples(year):
    y_vals = ['count']
    data_cat = value_per_month(app.adapter, year, y_vals, 'category')
    data_prio = value_per_month(app.adapter, year, y_vals, 'priority')
    y_axis_label = 'Nr of samples'

    return render_template('samples.html',
        header = 'Samples',
        page_id = 'samples',
        data_prio = data_prio['count'],
        data_cat = data_cat['count'],
        plot_prio = plot_attributes( title = 'Received samples per month (grouped by priority)' , y_axis_label = y_axis_label),
        plot_cat = plot_attributes( title = 'Received samples per month (grouped by application tag)' , y_axis_label = y_axis_label),
        year_of_interest=year,
        years = YEARS)


@blueprint.route('/prepps/microbial/<year>')
def microbial(year):
    y_vals = ['microbial_library_concentration']
    data = value_per_month(app.adapter, year, y_vals, "strain")
    return render_template('microbial.html',
        header = 'Microbial Samples',
        page_id = 'microbial',
        data = data['microbial_library_concentration'], 
        plot_attributes = plot_attributes( title = 'Microbial' , y_axis_label = 'Concentration (nM)'),
        year_of_interest=year,
        years = YEARS)


@blueprint.route('/prepps/target_enrichment/<year>')
def target_enrichment(year):
    y_vals = ['library_size_post_hyb', 'library_size_pre_hyb']
    data = value_per_month(app.adapter, year, y_vals, "source")
    y_axis_label = 'library size'

    return render_template('target_enrichment.html',
        header = 'Target Enrichment (exom/panels)',
        page_id = 'target_enrichment',
        data_pre_hyb = data['library_size_pre_hyb'],
        data_post_hyb = data['library_size_post_hyb'],
        plot_post_hyb = plot_attributes( title = 'Post-hybridization QC' , y_axis_label = y_axis_label),
        plot_pre_hyb = plot_attributes( title = 'Pre-hybridization QC' , y_axis_label = y_axis_label),
        year_of_interest=year,
        years = YEARS)


@blueprint.route('/prepps/wgs/<year>')
def wgs(year):
    concentration_time = value_per_month(app.adapter, year, ['nr_defrosts-concentration'])
    concentration_defrosts = find_concentration_defrosts(adapter = app.adapter, year = year)

    return render_template('wgs.html',
        header = 'WGS illumina PCR-free',
        page_id = 'wgs',
        concentration_defrosts = concentration_defrosts,
        concentration_time = concentration_time['nr_defrosts-concentration'],
        plot_attributes = plot_attributes( title = 'WGS illumina PCR-free' , y_axis_label = 'Concentration (nM)'),
        year_of_interest=year,
        years = YEARS)


@blueprint.route('/prepps/lucigen/<year>')
def lucigen(year):
    amount_concentration_time = value_per_month(app.adapter, year, ['amount-concentration'])
    concentration_amount = find_concentration_amount(adapter = app.adapter, year = year)

    return render_template('lucigen.html',
        header = 'Lucigen PCR-free',
        page_id = 'lucigen',
        amount_concentration_time = amount_concentration_time['amount-concentration'],
        plot_conc_time = plot_attributes( title = 'Lucigen PCR-free, Average Library concentration over time', y_axis_label = 'Concentration (nM)'),
        plot_amount_conc = plot_attributes(title = 'Lucigen PCR-free, Library concentration vs Input amount', y_axis_label = 'Concentration (nM)', x_axis_label = 'Amount (ng)'),
        amount = concentration_amount,
        year_of_interest=year,
        years = YEARS)


@blueprint.route('/sequencing/runs/<year>')
def runs(year):
    aggregate_result = q30_instruments(app.adapter, year)

    return render_template('runs.html',
        header = 'Sequencing Instruments',
        page_id = 'runs',
        results = aggregate_result,
        year_of_interest=year,
        years = YEARS)

@blueprint.route('/QC/mip_picard_time/<year>', methods=['GET', 'POST'])
def mip_picard_time(year):
    mip_results = mip_picard_time_plot(app.adapter, year)
    selcted_metric = request.form.get('picard_metric')
    if not selcted_metric:
        selcted_metric = 'MEAN_INSERT_SIZE'
    return render_template('mip_picard_time.html',
        selcted_metric = selcted_metric,
        mip_results = mip_results,
        PICARD_INSERT_SIZE = PICARD_INSERT_SIZE, 
        PICARD_HS_METRIC = PICARD_HS_METRIC,
        header = 'MIP',
        page_id = 'mip_picard_time',
        year_of_interest=year,
        years = YEARS)

@blueprint.route('/QC/mip_picard/<year>', methods=['GET', 'POST'])
def mip_picard(year):
   
    mip_results = mip_picard_plot(app.adapter, year)
    Y_axis = request.form.get('Y_axis', 'MEAN_INSERT_SIZE')
    X_axis = request.form.get('X_axis', 'MEAN_INSERT_SIZE')
    return render_template('mip_picard.html',
        Y_axis = Y_axis,
        X_axis = X_axis,
        mip_results = mip_results,
        PICARD_INSERT_SIZE = PICARD_INSERT_SIZE, 
        PICARD_HS_METRIC = PICARD_HS_METRIC,
        header = 'MIP',
        page_id = 'mip_picard',
        year_of_interest=year,
        years = YEARS)

@blueprint.route('/QC/balsamic/<year>')
def balsamic(year):

    return render_template('balsamic.html',
        header = 'Balsamic',
        page_id = 'balsamic',
        year_of_interest=year,
        years = YEARS)


@blueprint.route('/QC/microsalt/strain_st/<year>',  methods=['GET', 'POST'])
def microsalt_strain_st(year):
    strain = request.form.get('strain', '')
    results = microsalt_get_strain_st(app.adapter, year)
    return render_template('microsalt_strain_st.html',
        data = results.get(strain, {}),
        strain = strain,
        categories = results.keys(),
        header = 'Microsalt',
        page_id = 'strain_st',
        year_of_interest=year,
        years = YEARS)


@blueprint.route('/QC/microsalt/qc_time/<year>',  methods=['GET', 'POST'])
def microsalt_qc_time(year):
    metric_path = request.form.get('qc_metric', 'picard_markduplicate.insert_size')
    results = microsalt_get_qc_time(app.adapter, year , metric_path)
    return render_template('microsalt_qc_time.html',
        results = results['data'],
        categories = results['labels'],
        mean = results['mean'],
        selected_group = metric_path.split('.')[0],
        selected_metric = metric_path.split('.')[1],
        header = 'Microsalt',
        page_id = 'microsalt_qc_time',
        year_of_interest=year,
        MICROSALT = MICROSALT,
        years = YEARS)



@blueprint.route('/QC/microsalt/untyped/<year>',  methods=['GET', 'POST'])
def microsalt_untyped(year):
    results = microsalt_get_untyped(app.adapter, year )
    return render_template('microsalt_untyped.html',
        results = results['data'],
        categories = results['labels'],
        header = 'Microsalt',
        page_id = 'microsalt_untyped',
        year_of_interest=year,
        MICROSALT = MICROSALT,
        years = YEARS)


@blueprint.route('/QC/microsalt/st_time/<year>',  methods=['GET', 'POST'])
def microsalt_st_time(year):
    strain = request.form.get('strain', 'E.coli')
    results_all = microsalt_get_st_time(app.adapter, year )
    strain_results = results_all['data'].get(strain, {})
    return render_template('microsalt_st_time.html',
        results = strain_results,
        results_sorted_keys = sorted(strain_results.keys()),
        strain = strain,
        strains = results_all['data'].keys(),
        categories = results_all['labels'],
        header = 'Microsalt',
        page_id = 'microsalt_st_time',
        year_of_interest=year,
        MICROSALT = MICROSALT,
        years = YEARS)

@blueprint.route('/sequencing/hiseqx/<year>')
def hiseqx(year):

    return render_template('hiseqx.html',
        header = 'HiseqX',
        page_id = 'hiseqx',
        year_of_interest=year,
        years = YEARS)
