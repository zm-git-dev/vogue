#!/usr/bin/env python

from flask import render_template, Blueprint, current_app

from vogue.constants.constants import THIS_YEAR
from vogue.server.utils.reagent_labels import reagent_label_data, reagent_category_data
from vogue import __version__

app = current_app
index_blueprint = Blueprint('index', __name__)


@index_blueprint.route('/reagent_labels/<index_category_url>',
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


@index_blueprint.route('/reagent_label/<index_category>/<reagent_label>',
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
