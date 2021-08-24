#!/usr/bin/env python

from flask import url_for, redirect, render_template, request, Blueprint, current_app

from vogue.constants.constants import MONTHS, YEARS, THIS_YEAR
from vogue.server.utils.home import home_samples, home_customers
from vogue import __version__

app = current_app
home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/redirect", methods=["GET", "POST"])
def index():
    year = request.form.get("year", str(THIS_YEAR))
    endpoint = request.form.get("endpoint")

    if endpoint == "index.reagent_labels":
        index_category = request.form.get("index_category")
        index_category_url = index_category.replace(" ", "_")
        return redirect(url_for(endpoint, index_category_url=index_category_url))
    elif endpoint == "index.reagent_label":
        name, category = request.form.get("reagent_label").split(",")
        return redirect(
            url_for(endpoint, reagent_label=name.replace(" ", ""), index_category=category)
        )
    elif endpoint:
        return redirect(url_for(endpoint, year=year))


@home_blueprint.route("/", methods=["GET", "POST"])
def home():
    year = request.form.get("year", str(THIS_YEAR))
    endpoint = request.form.get("endpoint")
    month = int(request.form.get("month", 0))
    sample_series, cathegories = home_samples(app.adapter, int(year), month)
    customers = home_customers(app.adapter, int(year), month)

    return render_template(
        "index.html",
        version=__version__,
        sample_series=sample_series,
        cathegories=cathegories,
        customers=customers,
        endpoint=request.endpoint,
        year_of_interest=year,
        month_of_interest=month,
        months=MONTHS,
        month_name=MONTHS[month - 1][1] if month else "",
        years=YEARS,
    )
