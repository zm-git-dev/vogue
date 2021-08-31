#!/usr/bin/env python

from flask import render_template, Blueprint, current_app, request

from vogue.constants.constants import MONTHS, YEARS
from vogue.server.utils.metric_per_month import value_per_month
from vogue.server.utils.prepps import find_concentration_defrosts, find_concentration_amount
from vogue import __version__

app = current_app
prepps_blueprint = Blueprint("prepps", __name__)


@prepps_blueprint.route("/prepps/microbial/<year>")
def microbial(year: int):
    data = value_per_month(app.adapter, year, "microbial_library_concentration", "strain")

    return render_template(
        "microbial.html",
        header="Microbial Samples",
        endpoint=request.endpoint,
        data=data,
        months=[m[1] for m in MONTHS],
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )


@prepps_blueprint.route("/prepps/target_enrichment/<year>")
def target_enrichment(year: int):
    library_size_post_hyb = value_per_month(app.adapter, year, "library_size_post_hyb", "source")
    library_size_pre_hyb = value_per_month(app.adapter, year, "library_size_pre_hyb", "source")

    return render_template(
        "target_enrichment.html",
        header="Target Enrichment (exom/panels)",
        endpoint=request.endpoint,
        data_pre_hyb=library_size_pre_hyb,
        data_post_hyb=library_size_post_hyb,
        months=[m[1] for m in MONTHS],
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )


@prepps_blueprint.route("/prepps/wgs/<year>")
def wgs(year: int):
    concentration_time = value_per_month(app.adapter, year, "nr_defrosts-concentration")
    concentration_defrosts = find_concentration_defrosts(adapter=app.adapter, year=year)

    return render_template(
        "wgs.html",
        header="WGS illumina PCR-free",
        endpoint=request.endpoint,
        concentration_defrosts=concentration_defrosts,
        concentration_time=concentration_time,
        months=[m[1] for m in MONTHS],
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )


@prepps_blueprint.route("/prepps/lucigen/<year>")
def lucigen(year: int):
    amount_concentration_time = value_per_month(app.adapter, year, "amount-concentration")
    concentration_amount = find_concentration_amount(adapter=app.adapter, year=year)

    return render_template(
        "lucigen.html",
        header="Lucigen PCR-free",
        endpoint=request.endpoint,
        amount_concentration_time=amount_concentration_time,
        months=[m[1] for m in MONTHS],
        amount=concentration_amount,
        version=__version__,
        year_of_interest=year,
        years=YEARS,
    )
