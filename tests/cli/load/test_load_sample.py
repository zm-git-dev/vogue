from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter
from datetime import date, timedelta

app = create_app(test= True)

def test_sample_days(database, lims):
    # GIVEN a app context with a mock lims with a process 

    # database with a apptag in the application tag collection:
    database.application_tag.update_one({'_id' : 'WGSPCFC030'}, 
                                        {'$set' : {"category" : "wgs"}},
                                         upsert=True)

    # a lims with a lims sample
    lims_sample = lims._add_sample(sample_id='sample')                                
    lims_sample.udf['Sequencing Analysis'] = 'WGSPCFC030'

    # and a artifact related to the sample
    artifact = lims._add_artifact(samples = [lims_sample])

    # that was input to a process that was modifyed 3 days ago
    process = lims._add_process()
    process.inputs.append(artifact)
    three_days_ago = date.today() - timedelta(days=3)
    process.modified = three_days_ago.strftime("%Y-%m-%dT00:00:00Z")


    adapter = VougeAdapter(database.client, db_name = database.name)
    app.adapter = adapter
    app.db = database
    app.lims = lims

    # WHEN adding all samples modified within the last 4 days
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'sample', '-d', 4])

    # THEN the sample was added
    assert app.adapter.sample_collection.count() == 1

def test_sample_wrong_days():
    # GIVEN a app context

    # WHEN trying to tun the cli with incorect argument format for -d 
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'sample', '-d', 'U'])

    # THEN the program exits
    assert result.exit_code == 2

def test_sample_all(database, lims):
    # GIVEN a app context with a mock lims with a process 

    # database with a apptag in the application tag collection:
    database.application_tag.update_one({'_id' : 'WGSPCFC030'}, 
                                        {'$set' : {"category" : "wgs"}},
                                         upsert=True)

    # a lims with a lims sample   
    lims_sample = lims._add_sample(sample_id='sample')                               
    lims_sample.udf['Sequencing Analysis'] = 'WGSPCFC030'

    # and a artifact related to the sample
    artifact = lims._add_artifact(samples = [lims_sample])

    # that was input to a process that was modifyed 3 days ago
    process = lims._add_process()
    process.inputs.append(artifact)
    three_days_ago = date.today() - timedelta(days=3)
    process.modified = three_days_ago.strftime("%Y-%m-%dT00:00:00Z")

    print(lims.get_samples())
    adapter = VougeAdapter(database.client, db_name = database.name)
    app.adapter = adapter
    app.db = database
    app.lims = lims

    # WHEN adding all samples modified within the last 4 days
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'sample', '-a'])

    # THEN the sample was added
    assert app.adapter.sample_collection.count() == 1


