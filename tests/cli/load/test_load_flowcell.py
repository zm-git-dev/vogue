from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter
from vogue.constants.constants import RUN_TYPES, INSTRUMENTS

app = create_app(test= True)

def test_flowcell(database, lims):
    ## GIVEN a app context with a mock lims with a process of correct type and udf 
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)
    run_id = '190301_A00621_0010_AHHNTLDSXX'
    process_type = lims._add_process_type(name = RUN_TYPES[0])
    lims_run = lims._add_process(process_type = process_type)
    lims_run.udf = {'Run ID':run_id}
    app.lims = lims

    ## WHEN adding a flowcell to the flowcell collection
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', run_id])

    ## THEN a flowcell was created
    assert app.adapter.flowcell(run_id)['instrument'] == INSTRUMENTS['A00621']

def test_flowcell_no_lims(database):
    ## GIVEN a app context with no lims connection 
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)
    app.lims = None

    ## WHEN adding a flowcell tags
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', '190301_A00621_0010_AHHNTLDSXX'])

    ## THEN abort
    assert result.exit_code == 1


def test_flowcell_wrong_id(database, lims):
    ## GIVEN a app context with a lims connection 
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name = database.name)
    app.lims = lims

    ## WHEN adding a flowcell with a Run ID that does not exist in lims
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', '190301_A00621_0010_AHHNTLDSXX'])

    ## THEN abort
    assert result.exit_code == 1


 
