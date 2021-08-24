#!/usr/bin/env python

from flask import render_template, request, Blueprint, current_app

from vogue.constants.constants import YEARS, BIOINFO_HELP_URLS, DNA_PICARD, MONTHS
from vogue.server.utils.bioinfo.qc import qc_dna_picard_plot, qc_dna_picard_time_plot
from vogue import __version__

app = current_app
qc_blueprint = Blueprint("qc", __name__)


@qc_blueprint.route("/Bioinfo/picard_time/<year>", methods=["GET", "POST"])
def qc_dna_picard_time(year: int):
    qc_dna_results: List[dict] = qc_dna_picard_time_plot(app.adapter, year)
    selected_group, selcted_metric = request.form.get(
        "picard_metric", "PICARD_INSERT_SIZE MEAN_INSERT_SIZE"
    ).split()
    return render_template(
        "qc_over_time.html",
        selected_group=selected_group,
        selcted_metric=selcted_metric,
        qc_dna_results=qc_dna_results,
        DNA_PICARD=DNA_PICARD,
        help_urls=BIOINFO_HELP_URLS,
        months=[m[1] for m in MONTHS],
        header="QC over time",
        endpoint=request.endpoint,
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )


@qc_blueprint.route("/Bioinfo/picard/<year>", methods=["GET", "POST"])
def qc_dna_picard(year: int):
    qc_dna_results: List[dict] = qc_dna_picard_plot(app.adapter, year)
    Y_group, Y_axis = request.form.get("Y_axis", "PICARD_INSERT_SIZE MEAN_INSERT_SIZE").split()
    X_group, X_axis = request.form.get("X_axis", "PICARD_INSERT_SIZE MEAN_INSERT_SIZE").split()
    return render_template(
        "qc_dna_picard.html",
        Y_axis=Y_axis,
        X_axis=X_axis,
        groups=list(set([Y_group, X_group])),
        qc_dna_results=qc_dna_results,
        DNA_PICARD=DNA_PICARD,
        help_urls=BIOINFO_HELP_URLS,
        header="QC plots",
        endpoint=request.endpoint,
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )
