#!/usr/bin/env python

from flask import render_template, Blueprint, current_app, request

from vogue.constants.constants import THIS_YEAR
from vogue.server.utils.reagent_labels import reagent_label_data, reagent_category_data
from vogue import __version__

app = current_app
index_blueprint = Blueprint("index", __name__)
flowcell_performance_treshold = 0.3


@index_blueprint.route("/reagent_labels/<index_category_url>", methods=["GET", "POST"])
def reagent_labels(index_category_url: str):
    index_category = index_category_url.replace("_", " ")

    aggregate_result = reagent_category_data(
        app.adapter, index_category, flowcell_performance_treshold
    )
    return render_template(
        "reagent_labels.html",
        flowcell_performance_treshold=flowcell_performance_treshold,
        header="Overall performance per index",
        endpoint=request.endpoint,
        nr_indexes=len(aggregate_result),
        index_category=index_category,
        index_categories=app.adapter.get_reagent_label_categories(),
        year_of_interest=THIS_YEAR,
        results=aggregate_result,
        version=__version__,
    )


@index_blueprint.route("/reagent_label/<index_category>/<reagent_label>", methods=["GET", "POST"])
def reagent_label(index_category: str, reagent_label: str):
    aggregate_result = reagent_label_data(app.adapter, reagent_label, flowcell_performance_treshold)
    index_categories = list(app.adapter.get_all_reagent_label_names_grouped_by_category())
    return render_template(
        "reagent_label.html",
        endpoint=request.endpoint,
        flowcell_performance_treshold=flowcell_performance_treshold,
        header="Normalized index performance per flowcell",
        index_category=index_category.replace("_", " "),
        year_of_interest=THIS_YEAR,
        reagent_label=reagent_label,
        index_categories=index_categories,
        results=aggregate_result,
        version=__version__,
    )
