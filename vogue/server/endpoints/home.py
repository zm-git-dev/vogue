#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app

from vogue.constants.constants import MONTHS, YEARS, THIS_YEAR
from vogue.server.utils.home import home_samples, home_customers
from vogue import __version__

app = current_app
home_blueprint = Blueprint('home', __name__)

@home_blueprint.route('/', methods=['GET', 'POST'])
def index():
    year = request.form.get('year', str(THIS_YEAR))
    if request.form.get('page') == 'turn_around_times':
        return redirect(url_for('common_trends.turn_around_times', year=year))
    if request.form.get('page') == 'samples':
        return redirect(url_for('common_trends.common_samples', year=year))
    if request.form.get('page') == 'microbial':
        return redirect(url_for('prepps.microbial', year=year))
    if request.form.get('page') == 'wgs':
        return redirect(url_for('prepps.wgs', year=year))
    if request.form.get('page') == 'lucigen':
        return redirect(url_for('prepps.lucigen', year=year))
    if request.form.get('page') == 'target_enrichment':
        return redirect(url_for('prepps.target_enrichment', year=year))
    if request.form.get('page') == 'runs':
        return redirect(url_for('sequencing.runs', year=year))
    if request.form.get('page') == 'mip_dna_picard_time':
        return redirect(url_for('mip.dna_picard_time', year=year))
    if request.form.get('page') == 'mip_dna_picard':
        return redirect(url_for('mip.dna_picard', year=year))
    if request.form.get('page') == 'strain_st':
        return redirect(url_for('micro.strain_st', year=year))
    if request.form.get('page') == 'microsalt_qc_time':
        return redirect(url_for('micro.qc_time', year=year))
    if request.form.get('page') == 'microsalt_untyped':
        return redirect(url_for('micro.untyped', year=year))
    if request.form.get('page') == 'microsalt_st_time':
        return redirect(url_for('micro.st_time', year=year))
    if request.form.get('page') == 'microsalt_cov_qc_time':
        return redirect(url_for('covid.microsalt_qc_time', year=year))
    if request.form.get('page') == 'cov_qc_scatter':
        return redirect(url_for('covid.qc_scatter', year=year))
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
                           cathegories=cathegories,
                           customers=customers,
                           page_id='index',
                           year_of_interest=year,
                           month_of_interest=month,
                           months=MONTHS,
                           month_name=MONTHS[month - 1][1] if month else '',
                           years=YEARS)