from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter
from datetime import date, timedelta

app = create_app(test= True)

def test_sample(lims_sample, database, lims):
    # GIVEN a app context with a mock lims with a process 

    # database with a apptag in the application tag collection:
    database.application_tag.update_one({'_id' : 'WGSPCFC030'}, 
                                        {'$set' : {"category" : "wgs"}},
                                         upsert=True)

    # a lims with a lims sample                                  
    lims_sample.udf['Sequencing Analysis'] = 'WGSPCFC030'
    
    
    #process_type = lims._add_process_type(name = 'HEJ')
    process = lims._add_process()#process_type = process_type)
    three_days_ago = date.today() - timedelta(days=3)
    process.modified = three_days_ago.strftime("%Y-%m-%dT00:00:00Z")

    artifact = lims._add_artifact(samples = [lims_sample])

    
    
    process.inputs.append(artifact)

    adapter = VougeAdapter(database.client, db_name = database.name)
    app.adapter = adapter
    app.db = database
    app.lims = lims

    # WHEN adding all samples modified within the last 4 days
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'sample', '-d', 4])

    # THEN the sample was added
    assert app.adapter.sample_collection.count() == 1