#!/usr/bin/env python

from flask import render_template, request, Blueprint, current_app

from vogue.constants.constants import THIS_YEAR
from vogue.server.utils.genotype import get_genotype_plate
from vogue import __version__

app = current_app
genotype_blueprint = Blueprint("genotype", __name__)


@genotype_blueprint.route("/Bioinfo/Genotype/plate", methods=["GET", "POST"])
def genotype_plate():
    plate_id = request.form.get("plate_id")
    plot_data = get_genotype_plate(app.adapter, plate_id=plate_id)
    plot_data["plates"].sort()
    return render_template(
        "genotype_plate.html",
        plate_data=plot_data["data"],
        x_labels=plot_data["x_labels"],
        y_labels=plot_data["y_labels"],
        year_of_interest=str(THIS_YEAR),
        header="Genotype",
        page_id="genotype_plate",
        version=__version__,
        plate_id=plot_data["plate_id"],
        plates=plot_data["plates"],
    )
