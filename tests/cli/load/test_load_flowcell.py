from vogue.server import create_app
from vogue.commands.base import cli
from vogue.adapter.plugin import VougeAdapter
from vogue.constants.constants import RUN_TYPES, INSTRUMENTS
from datetime import date, timedelta

app = create_app(test=True)


def test_flowcell(database, lims):
    # GIVEN a app context with a mock lims with a process of correct type and udf
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    run_id = '190301_A00621_0010_AHHNTLDSXX'
    process_type = lims._add_process_type(name=RUN_TYPES[0])
    lims_run = lims._add_process(process_type=process_type)
    lims_run.udf = {'Run ID': run_id}
    app.lims = lims

    # WHEN adding a flowcell to the flowcell collection
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', run_id])

    # THEN a flowcell was created
    assert app.adapter.flowcell(run_id)['instrument'] == INSTRUMENTS['A00621']


def test_flowcell_no_instrument_name(database, lims):
    # GIVEN a app context with a mock lims with a process of correct type and udf
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    run_id = '19001_A021_010_AHHLDSXX'
    process_type = lims._add_process_type(name=RUN_TYPES[0])
    lims_run = lims._add_process(process_type=process_type)
    lims_run.udf = {'Run ID': run_id}
    app.lims = lims

    # WHEN adding a flowcell to the flowcell collection
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', run_id])

    # THEN no flowcell was created
    assert app.adapter.flowcell(run_id) is None


def test_flowcell_missing_RUN_ID(database, lims):
    # GIVEN a app context with a mock lims with a process of correct type and udf
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    run_id = '190301_A00621_0010_AHHNTLDSXX'
    process_type = lims._add_process_type(name=RUN_TYPES[0])
    lims_run = lims._add_process(process_type=process_type)
    app.lims = lims

    # WHEN adding a flowcell to the flowcell collection
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', run_id])

    # THEN no flowcell was created
    assert result.exit_code == 1
    assert app.adapter.flowcell(run_id) is None


def test_flowcell_no_lims(database):
    # GIVEN a app context with no lims connection
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    app.lims = None

    # WHEN adding a flowcell tags
    runner = app.test_cli_runner()
    result = runner.invoke(
        cli, ['load', 'flowcell', '-r', '190301_A00621_0010_AHHNTLDSXX'])

    # THEN abort
    assert result.exit_code == 1


def test_flowcell_wrong_id(database, lims):
    # GIVEN a app context with a lims connection
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    app.lims = lims

    # WHEN adding a flowcell with a Run ID that does not exist in lims
    runner = app.test_cli_runner()
    result = runner.invoke(
        cli, ['load', 'flowcell', '-r', '190301_A00621_0010_AHHNTLDSXX'])

    # THEN abort
    assert result.exit_code == 1


def test_flowcell_two_runs_one_id(database, lims):
    # GIVEN a app context with a mock lims with two processes with the same run id
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    process_type = lims._add_process_type(name=RUN_TYPES[0])
    run_id = '190301_A00621_0010_AHHNTLDSXX'
    lims_run1 = lims._add_process(process_type=process_type)
    lims_run1.udf = {'Run ID': run_id}
    lims_run2 = lims._add_process(process_type=process_type)
    lims_run2.udf = {'Run ID': run_id}
    app.lims = lims

    # WHEN running load flowcell with that run_id
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-r', run_id])

    # THEN one of the processes are added
    assert app.adapter.flowcell(run_id)['instrument'] == INSTRUMENTS['A00621']


def test_flowcell_days(database, lims):
    # GIVEN a app context with a mock lims with a processes modified 3 vs 5 days ago
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    run_id1 = '190301_A00621_0010_AHHNTLDSXX'
    run_id2 = '190301_A00689_0010_AHHNTLDSXX'
    process_type = lims._add_process_type(name=RUN_TYPES[0])
    run1 = lims._add_process(process_type=process_type)
    run1.udf = {'Run ID': run_id1}
    three_days_ago = date.today() - timedelta(days=3)
    run1.modified = three_days_ago.strftime("%Y-%m-%dT00:00:00Z")
    run2 = lims._add_process(process_type=process_type)
    run2.udf = {'Run ID': run_id2}
    five_days_ago = date.today() - timedelta(days=5)
    run2.modified = five_days_ago.strftime("%Y-%m-%dT00:00:00Z")
    app.lims = lims

    # WHEN adding all flowcells modified within the last 4 days
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-d', 4])

    # THEN only one of the flowcells are added
    assert app.adapter.flowcell(run_id1)['instrument'] == INSTRUMENTS['A00621']
    assert app.adapter.flowcell(run_id2) is None


def test_flowcell_days_wrong_type(database, lims):
    # GIVEN a app context with a mock lims
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    app.lims = lims

    # WHEN running load flowcell -d with wrong type of argument
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-d', 'apa'])

    # THEN exit
    assert result.exit_code == 2


def test_flowcell_all(database, lims):
    # GIVEN a app context with a mock lims with two run processes
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    process_type = lims._add_process_type(name=RUN_TYPES[0])
    run_id1 = '190301_A00621_0010_AHHNTLDSXX'
    run_id2 = '190301_A00689_0010_AHHNTLDSXX'
    lims_run1 = lims._add_process(process_type=process_type)
    lims_run1.udf = {'Run ID': run_id1}
    lims_run2 = lims._add_process(process_type=process_type)
    lims_run2.udf = {'Run ID': run_id2}
    app.lims = lims

    # WHEN  running load flowcell -a
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'flowcell', '-a'])

    # THEN both runs are added
    assert app.adapter.flowcell(run_id1)['instrument'] == INSTRUMENTS['A00621']
    assert app.adapter.flowcell(run_id2)['instrument'] == INSTRUMENTS['A00689']
