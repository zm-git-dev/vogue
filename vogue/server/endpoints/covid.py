#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app

from vogue.constants.constants import *
from vogue.server.utils import *
from vogue.server.utils.covid import get_qc
from vogue import __version__

app = current_app
covid_blueprint = Blueprint('covid', __name__)


HEADER= 'Microsalt Covid'


@covid_blueprint.route('/Bioinfo/Covid/qc_time/<year>', methods=['GET', 'POST'])
def microsalt_qc_time(year):
    metric_path = request.form.get('qc_metric',
                                   'picard_markduplicate.insert_size')
    results = microsalt_get_qc_time(app.adapter, year=year, metric_path=metric_path, category='cov')
    return render_template('microsalt_qc_time.html',
                           results=results['data'],
                           categories=results['labels'],
                           mean=results['mean'],
                           selected_group=metric_path.split('.')[0],
                           selected_metric=metric_path.split('.')[1],
                           header=HEADER,
                           page_id='microsalt_cov_qc_time',
                           page_url='covid.microsalt_qc_time',
                           version=__version__,
                           year_of_interest=year,
                           MICROSALT=MICROSALT,
                           years=YEARS)



@covid_blueprint.route('/Bioinfo/Covid/qc_time_scatter/<year>', methods=['GET', 'POST'])
def qc_scatter(year):
    metric_path = request.form.get('qc_metric',
                                   'picard_markduplicate.insert_size')
    results = get_qc(app.adapter, year=year, metric_path=metric_path)

    return render_template('cov_qc_scatter.html',
                           results=results,
                           MICROSALT=MICROSALT,
                           selected_group=metric_path.split('.')[0],
                           metric=metric_path.split('.')[1],
                           header=HEADER,
                           page_id='cov_qc_scatter',
                           page_url='covid.qc_scatter',
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)

