#!/usr/bin/env python

from flask import render_template, request, Blueprint, current_app

from vogue.constants.constants import YEARS, MICROSALT
from vogue.server.utils.bioinfo.micro import (
    microsalt_get_untyped,
    microsalt_get_st_time,
    microsalt_get_qc_time,
    microsalt_get_strain_st,
)
from vogue import __version__

app = current_app
micro_blueprint = Blueprint("micro", __name__)


@micro_blueprint.route("/Bioinfo/Microbial/strain_st/<year>", methods=["GET", "POST"])
def strain_st(year: int):
    results = microsalt_get_strain_st(app.adapter, year)
    strain = request.form.get("strain", "")
    if results and not strain:
        strain = list(results.keys())[0]

    return render_template(
        "microsalt_strain_st.html",
        data=results.get(strain, {}),
        strain=strain,
        endpoint=request.endpoint,
        categories=results.keys(),
        header="Microsalt",
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )


@micro_blueprint.route("/Bioinfo/Microbial/qc_time/<year>", methods=["GET", "POST"])
def qc_time(year: int):
    metric_path = request.form.get("qc_metric", "picard_markduplicate.insert_size")
    results = microsalt_get_qc_time(app.adapter, year=year, metric_path=metric_path, category="mic")

    return render_template(
        "microsalt_qc_time.html",
        results=results["data"],
        outliers=results["outliers"],
        categories=results["labels"],
        mean=results["mean"],
        endpoint=request.endpoint,
        selected_group=metric_path.split(".")[0],
        selected_metric=metric_path.split(".")[1],
        header="Microsalt",
        version=__version__,
        year_of_interest=year,
        MICROSALT=MICROSALT,
        years=YEARS,
    )


@micro_blueprint.route("/Bioinfo/Microbial/untyped/<year>", methods=["GET", "POST"])
def untyped(year: int):
    results = microsalt_get_untyped(app.adapter, year)

    return render_template(
        "microsalt_untyped.html",
        results=results["data"],
        categories=results["labels"],
        header="Microsalt",
        endpoint=request.endpoint,
        version=__version__,
        year_of_interest=year,
        MICROSALT=MICROSALT,
        years=YEARS,
    )


@micro_blueprint.route("/Bioinfo/Microbial/st_time/<year>", methods=["GET", "POST"])
def st_time(year: int):
    strain = request.form.get("strain", "")
    results_all = microsalt_get_st_time(app.adapter, year)
    if results_all["data"] and not strain:
        strain = list(results_all["data"].keys())[0]
    strain_results = results_all["data"].get(strain, {})

    return render_template(
        "microsalt_st_time.html",
        results=strain_results,
        results_sorted_keys=sorted(strain_results.keys()),
        strain=strain,
        endpoint=request.endpoint,
        strains=results_all["data"].keys(),
        categories=results_all["labels"],
        header="Microsalt",
        version=__version__,
        year_of_interest=year,
        MICROSALT=MICROSALT,
        years=YEARS,
    )
