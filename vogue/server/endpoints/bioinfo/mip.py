#!/usr/bin/env python

from flask import render_template, request, Blueprint, current_app

from vogue.constants.constants import YEARS, BIOINFO_HELP_URLS, MIP_DNA_PICARD, MONTHS
from vogue.server.utils.bioinfo.mip import mip_dna_picard_plot, mip_dna_picard_time_plot
from vogue.server.utils import *
from vogue import __version__

app = current_app
mip_blueprint = Blueprint('mip', __name__)




@mip_blueprint.route('/Bioinfo/Rare_Disease/picard_time/<year>',
                 methods=['GET', 'POST'])
def dna_picard_time(year):
    mip_dna_results = mip_dna_picard_time_plot(app.adapter, year)
    selected_group, selcted_metric = request.form.get(
        'picard_metric', 'PICARD_INSERT_SIZE MEAN_INSERT_SIZE').split()
    return render_template('mip_dna_picard_time.html',
                           selected_group=selected_group,
                           selcted_metric=selcted_metric,
                           mip_dna_results=mip_dna_results,
                           MIP_DNA_PICARD=MIP_DNA_PICARD,
                           help_urls=BIOINFO_HELP_URLS,
                           months=[m[1] for m in MONTHS],
                           header='MIP',
                           page_id='mip_dna_picard_time',
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)


@mip_blueprint.route('/Bioinfo/Rare_Disease/picard/<year>',
                 methods=['GET', 'POST'])
def dna_picard(year):
    mip_dna_results = mip_dna_picard_plot(app.adapter, year)
    Y_group, Y_axis = request.form.get(
        'Y_axis', 'PICARD_INSERT_SIZE MEAN_INSERT_SIZE').split()
    X_group, X_axis = request.form.get(
        'X_axis', 'PICARD_INSERT_SIZE MEAN_INSERT_SIZE').split()
    return render_template('mip_dna_picard.html',
                           Y_axis=Y_axis,
                           X_axis=X_axis,
                           groups=list(set([Y_group, X_group])),
                           mip_dna_results=mip_dna_results,
                           MIP_DNA_PICARD=MIP_DNA_PICARD,
                           help_urls=BIOINFO_HELP_URLS,
                           header='MIP',
                           page_id='mip_dna_picard',
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)
