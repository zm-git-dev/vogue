#!/usr/bin/env python

from flask import render_template, Blueprint, current_app

from vogue.constants.constants import *
from vogue.server.utils import *
from vogue import __version__

app = current_app
cancer_blueprint = Blueprint('cancer', __name__)


@cancer_blueprint.route('/Bioinfo/Cancer/<year>')
def balsamic(year):

    return render_template('balsamic.html',
                           header='Balsamic',
                           page_id='balsamic',
                           version=__version__,
                           year_of_interest=year,
                           years=YEARS)