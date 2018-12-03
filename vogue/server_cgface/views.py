from flask import make_response, flash, abort, url_for, redirect, render_template, request, session
from flask_login import login_user,logout_user, current_user, login_required
from flask.ext.mail import Message
from flask_oauthlib.client import OAuthException
from extentions import app
from vogue import PrepsCommon
from  datetime import date

THIS_YEAR = date.today().year
YEARS = [str(y) for y in range(2017, THIS_YEAR + 1)]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.form.get('common'):
        year = request.form.get('year')
        return redirect(url_for('common', year_of_interest=year))
    return render_template(
        'index.html',
        this_year = THIS_YEAR)

@app.route('/prepps/common/<year_of_interest>')
def common(year_of_interest):
    PC = PrepsCommon(year_of_interest)
    turnaround_times = PC.make_data('turnaround_times')
    received = PC.make_data('received')
    received_application = PC.make_data('received_application')
    return render_template('common.html',
        header = 'Common',
        received = received,
        received_application = received_application,
        turnaround_times = turnaround_times,
        year_of_interest=year_of_interest,
        this_year = THIS_YEAR,
        years = YEARS)

@app.route('/prepps/microbial/<year_of_interest>')
def microbial(year_of_interest):
    return render_template('microbial.html',
        header = 'Microbial Samples',
        year_of_interest=year_of_interest,
        this_year = THIS_YEAR,
        years = YEARS)


@app.route('/sequencing/novaseq/<year_of_interest>')
def novaseq(year_of_interest):
    return render_template('novaseq.html',
        header = 'Nova Seq',
        year_of_interest=year_of_interest,
        this_year = THIS_YEAR,
        years = YEARS)

@app.route('/sequencing/hiseqx/<year_of_interest>')
def hiseqx(year_of_interest):
    return render_template('hiseqx.html',
        header = 'HiseqX',
        year_of_interest=year_of_interest,
        this_year = THIS_YEAR,
        years = YEARS)

