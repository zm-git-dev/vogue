#!/usr/bin/env python

from flask import render_template, Blueprint, current_app

from vogue.constants.constants import MONTHS, YEARS
from vogue.server.utils.metric_per_month import value_per_month
from vogue import __version__

app = current_app
common_trends_blueprint = Blueprint('common_trends', __name__)


@common_trends_blueprint.route('/common/turn_around_times/<year>')
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


@common_trends_blueprint.route('/common/samples/<year>')
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

