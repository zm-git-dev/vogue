#!/usr/bin/env python

from flask import render_template, request, Blueprint, current_app

from vogue.constants.constants import MICROSALT, YEARS
from vogue.server.utils.bioinfo.micro import microsalt_get_qc_time
from vogue.server.utils.bioinfo.covid import get_qc
from vogue import __version__

app = current_app
covid_blueprint = Blueprint("covid", __name__)

HEADER = "Microsalt Covid"


@covid_blueprint.route("/Bioinfo/Covid/qc_time/<year>", methods=["GET", "POST"])
def microsalt_qc_time(year: int):
    """Box plot with qc data per month"""

    metric_path = request.form.get("qc_metric", "picard_markduplicate.insert_size")
    results = microsalt_get_qc_time(app.adapter, year=year, metric_path=metric_path, category="cov")
    return render_template(
        "microsalt_qc_time.html",
        results=results["data"],
        outliers=results["outliers"],
        categories=results["labels"],
        mean=results["mean"],
        selected_group=metric_path.split(".")[0],
        selected_metric=metric_path.split(".")[1],
        header=HEADER,
        endpoint=request.endpoint,
        version=__version__,
        year_of_interest=year,
        MICROSALT=MICROSALT,
        years=YEARS,
    )


@covid_blueprint.route("/Bioinfo/Covid/qc_time_scatter/<year>", methods=["GET", "POST"])
def qc_scatter(year: int):
    """Scatter plot with qc data over time, grouped by prep method"""

    metric_path = request.form.get("qc_metric", "picard_markduplicate.insert_size")
    results = get_qc(app.adapter, year=year, metric_path=metric_path)

    return render_template(
        "cov_qc_scatter.html",
        results=results,
        MICROSALT=MICROSALT,
        selected_group=metric_path.split(".")[0],
        metric=metric_path.split(".")[1],
        header=HEADER,
        endpoint=request.endpoint,
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )
