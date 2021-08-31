#!/usr/bin/env python

from flask import render_template, request, Blueprint, current_app

from vogue.constants.constants import LANE_UDFS, YEARS
from vogue.server.utils.sequencing import instrument_info
from vogue import __version__

app = current_app
sequencing_blueprint = Blueprint("sequencing", __name__)


@sequencing_blueprint.route("/sequencing/runs/<year>", methods=["GET", "POST"])
def runs(year: int):
    selcted_metric = request.form.get("metric", "% Bases >=Q30")
    aggregate_result = instrument_info(app.adapter, year, selcted_metric)

    return render_template(
        "runs.html",
        header="Sequencing Instruments",
        endpoint=request.endpoint,
        page_id="runs",
        metric=selcted_metric,
        metrices=LANE_UDFS,
        results=aggregate_result,
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )
