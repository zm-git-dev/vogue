from flask import  url_for, redirect, render_template, request
from vogue.constants.constants import YEARS, THIS_YEAR

from extentions import app
from vogue.server.utils import ( find_concentration_defrosts, find_concentration_amount,   
                                find_key_over_time, build_group_queries_from_key, 
                                build_app_tag_group_queries)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.form.get('page') == 'turn_around_times':
        year = request.form.get('year')
        return redirect(url_for('turn_around_times', year_of_interest=year))
    if request.form.get('page') == 'samples':
        year = request.form.get('year')
        return redirect(url_for('common_samples', year_of_interest=year))
    if request.form.get('page') == 'microbial':
        year = request.form.get('year')
        return redirect(url_for('microbial', year_of_interest=year))
    if request.form.get('page') == 'wgs':
        year = request.form.get('year')
        return redirect(url_for('wgs', year_of_interest=year))
    if request.form.get('page') == 'lucigen':
        year = request.form.get('year')
        return redirect(url_for('lucigen', year_of_interest=year))
    if request.form.get('page') == 'target_enrichment':
        year = request.form.get('year')
        return redirect(url_for('target_enrichment', year_of_interest=year))

    return render_template(
        'index.html',
        year_of_interest = THIS_YEAR)

@app.route('/common/turn_around_times/<year_of_interest>')
def turn_around_times(year_of_interest):
    app_tag_group_queries = build_app_tag_group_queries()
    prio_group_queries = build_group_queries_from_key("priority")

    received_to_delivered = {'tag' : find_key_over_time(
                                year = year_of_interest, 
                                group_queries = app_tag_group_queries, 
                                y_axis_key ='received_to_delivered', 
                                title = 'Time from recieved to delivered (grouped by application tag)', 
                                y_axis_label = 'Days', 
                                y_unit = 'average'),
                            'prio' : find_key_over_time(
                                year = year_of_interest, 
                                group_queries = prio_group_queries, 
                                y_axis_key ='received_to_delivered', 
                                title = 'Time from recieved to delivered (grouped by priority)', 
                                y_axis_label = 'Days', 
                                y_unit = 'average')}
    received_to_prepped = {'tag' : find_key_over_time(
                                year = year_of_interest, 
                                group_queries = app_tag_group_queries, 
                                y_axis_key ='received_to_prepped' , 
                                title = 'Time from recieved to prepped (grouped by application tag)', 
                                y_axis_label = 'Days', 
                                y_unit = 'average'),
                            'prio' : find_key_over_time(
                                year = year_of_interest, 
                                group_queries = prio_group_queries, 
                                y_axis_key ='received_to_prepped' , 
                                title = 'Time from recieved to prepped (grouped by priority)', 
                                y_axis_label = 'Days', 
                                y_unit = 'average')}
    prepped_to_sequenced = {'tag' : find_key_over_time(
                                year = year_of_interest, 
                                group_queries = app_tag_group_queries, 
                                y_axis_key ='prepped_to_sequenced' , 
                                title = 'Time from prepped to sequenced (grouped by application tag)', 
                                y_axis_label = 'Days', 
                                y_unit = 'average'),
                            'prio' : find_key_over_time(
                                year = year_of_interest, 
                                group_queries = prio_group_queries, 
                                y_axis_key ='prepped_to_sequenced' , 
                                title = 'Time from prepped to sequenced (grouped by priority)', 
                                y_axis_label = 'Days', 
                                y_unit = 'average')}
    sequenced_to_delivered = {'tag' : find_key_over_time(
                                year = year_of_interest, 
                                group_queries = app_tag_group_queries, 
                                y_axis_key ='sequenced_to_delivered', 
                                title = 'Time from sequenced to delivered (grouped by application tag)', 
                                y_axis_label = 'Days', 
                                y_unit = 'average'),
                            'prio' : find_key_over_time(
                                year = year_of_interest, 
                                group_queries = prio_group_queries, 
                                y_axis_key ='sequenced_to_delivered', 
                                title = 'Time from sequenced to delivered (grouped by priority)', 
                                y_axis_label = 'Days', 
                                y_unit = 'average')}
    
    return render_template('turn_around_times.html',
        header = 'Turn Around Times',
        page_id = 'turn_around_times',
        received_to_delivered = received_to_delivered,
        received_to_prepped = received_to_prepped,
        prepped_to_sequenced = prepped_to_sequenced,
        sequenced_to_delivered = sequenced_to_delivered,
        year_of_interest=year_of_interest,
        years = YEARS)


@app.route('/common/samples/<year_of_interest>')
def common_samples(year_of_interest):
    group_by = ['research','standard','priority']#,'express']
    group_queries = build_group_queries_from_key("priority")
    app_tag_group_queries = build_app_tag_group_queries()
    received = find_key_over_time(
                    year = year_of_interest, 
                    group_queries = group_queries, 
                    title = 'Received_application samples per month (grouped by priority)', 
                    y_axis_label = 'Nr of samples', 
                    y_unit = 'number samples')
    received_application = find_key_over_time(
                    year = year_of_interest, 
                    group_queries = app_tag_group_queries, 
                    title = 'Received_application samples per month (grouped by aplication tag)', 
                    y_axis_label = 'Days', 
                    y_unit = 'number samples')#wrong groups!!!

    return render_template('samples.html',
        header = 'Samples',
        page_id = 'samples',
        received = received,
        received_application = received_application,
        year_of_interest=year_of_interest,
        years = YEARS)


@app.route('/prepps/microbial/<year_of_interest>')
def microbial(year_of_interest):
    group_queries = build_group_queries_from_key("strain")
    microbial_concentration_time = find_key_over_time(
                                        year = year_of_interest, 
                                        group_queries = group_queries, 
                                        y_axis_key ='microbial_library_concentration', 
                                        title = 'Microbial',
                                        y_axis_label = 'Concentration (nM)',
                                        y_unit = 'average')

    return render_template('microbial.html',
        header = 'Microbial Samples',
        page_id = 'microbial',
        microbial_concentration_time = microbial_concentration_time,
        year_of_interest=year_of_interest,
        years = YEARS)


@app.route('/prepps/target_enrichment/<year_of_interest>')
def target_enrichment(year_of_interest):
    group_queries = build_group_queries_from_key("source")
    library_size_post_hyb = find_key_over_time(
                                year = year_of_interest, 
                                group_queries = group_queries, 
                                y_axis_key ='library_size_post_hyb', 
                                title = 'Post-hybridization QC', 
                                y_axis_label = 'library size',
                                y_unit = 'average')
    library_size_pre_hyb = find_key_over_time(
                                year = year_of_interest, 
                                group_queries = group_queries, 
                                y_axis_key ='library_size_pre_hyb', 
                                title = 'Pre-hybridization QC', 
                                y_axis_label = 'library size',
                                y_unit = 'average')

    return render_template('target_enrichment.html',
        header = 'Target enrichment (exom/panels)',
        page_id = 'target_enrichment',
        library_size_pre_hyb = library_size_pre_hyb,
        library_size_post_hyb = library_size_post_hyb,
        year_of_interest=year_of_interest,
        years = YEARS)


@app.route('/prepps/wgs/<year_of_interest>')
def wgs(year_of_interest):
    concentration_defrosts = find_concentration_defrosts(year = year_of_interest)
    concentration_time = find_key_over_time(
                            year = year_of_interest, 
                            y_axis_key ='nr_defrosts-concentration', 
                            title = 'wgs illumina PCR-free', 
                            y_axis_label = 'Concentration (nM)',
                            y_unit = 'average') #, by_month=False)
    return render_template('wgs.html',
        header = 'WGS illumina PCR-free',
        page_id = 'wgs',
        concentration_defrosts = concentration_defrosts,
        concentration_time = concentration_time,
        year_of_interest=year_of_interest,
        years = YEARS)


@app.route('/prepps/lucigen/<year_of_interest>')
def lucigen(year_of_interest):
    amount_concentration_time = find_key_over_time(year = year_of_interest, 
                                        y_axis_key ='amount-concentration', 
                                        title = 'lucigen PCR-free',
                                        y_axis_label = 'Concentration (nM)' ,
                                        y_unit = 'average')
    concentration_amount = find_concentration_amount(year = year_of_interest)
    return render_template('lucigen.html',
        header = 'Lucigen PCR-free',
        page_id = 'lucigen',
        amount_concentration_time = amount_concentration_time,
        amount = concentration_amount,
        year_of_interest=year_of_interest,
        years = YEARS)


@app.route('/sequencing/novaseq/<year_of_interest>')
def novaseq(year_of_interest):

    return render_template('novaseq.html',
        header = 'Nova Seq',
        page_id = 'novaseq',
        year_of_interest=year_of_interest,
        years = YEARS)


@app.route('/sequencing/hiseqx/<year_of_interest>')
def hiseqx(year_of_interest):

    return render_template('hiseqx.html',
        header = 'HiseqX',
        page_id = 'hiseqx',
        year_of_interest=year_of_interest,
        years = YEARS)

