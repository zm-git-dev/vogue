from vogue.build.flowcell import build_run
from datetime import datetime as dt


def test_build_run(lims):
    # GIVEN a run date, a instrument id and a lims_run with two lanes:
    L1 = lims._add_artifact()
    L2 = lims._add_artifact()
    process_type = lims._add_process_type(name='AUTOMATED - NovaSeq Run')
    lims_run = lims._add_process(process_type=process_type)
    L1.name = 'Lane 1'
    L2.name = 'Lane 2'
    L1.udf = {'% Bases >=Q30 R1': 90, '% Bases >=Q30 R2': 81}
    L2.udf = {'% Bases >=Q30 R1': 91, '% Bases >=Q30 R2': 82}
    L1.location = '1:1'
    L2.location = '1:2'
    lims_run.outputs = [L1, L2]
    lims_run.udf = {'Run ID': '190301_A00621_0010_AHHNTLDSXX'}
    date = '190301'
    instrument = 'A00621'

    # WHEN building the mongo_run:
    mongo_run = build_run(lims_run, instrument, date)

    # THEN assert lanes and avg was added. avg Q30== 86
    print(mongo_run)
    assert mongo_run == {
        '_id': '190301_A00621_0010_AHHNTLDSXX',
        'instrument': 'A00621',
        'date': dt(2019, 3, 1, 0, 0),
        'Run ID': '190301_A00621_0010_AHHNTLDSXX',
        'avg': {
            '% Bases >=Q30': 86.0,
            '% Bases >=Q30 R1': 90.5,
            '% Bases >=Q30 R2': 81.5
        },
        'lanes': {
            'Lane 1': {
                '% Bases >=Q30 R1': 90,
                '% Bases >=Q30 R2': 81
            },
            'Lane 2': {
                '% Bases >=Q30 R1': 91,
                '% Bases >=Q30 R2': 82
            }
        }
    }


def test_build_run_no_data(lims):
    # GIVEN a run date, a instrument id and a lims_run with no lanes:
    process_type = lims._add_process_type(name='AUTOMATED - NovaSeq Run')
    lims_run = lims._add_process(process_type=process_type)
    lims_run.udf = {'Run ID': '190301_A00621_0010_AHHNTLDSXX'}
    date = '190301'
    instrument = 'A00621'

    # WHEN building the mongo_run:
    mongo_run = build_run(lims_run, instrument, date)

    # THEN assert no lanes or avg were added to the mongo_run
    assert mongo_run == {
        '_id': '190301_A00621_0010_AHHNTLDSXX',
        'instrument': 'A00621',
        'date': dt(2019, 3, 1, 0, 0),
        'Run ID': '190301_A00621_0010_AHHNTLDSXX',
        'avg': {},
        'lanes': {}
    }


def test_build_run_no_instrument(lims):
    # GIVEN a run date, a instrument id and a lims_run with no lanes:
    process_type = lims._add_process_type(name='AUTOMATED - NovaSeq Run')
    lims_run = lims._add_process(process_type=process_type)
    lims_run.udf = {}
    date = '190301'
    instrument = None

    # WHEN building the mongo_run:
    mongo_run = build_run(lims_run, instrument, date)

    # THEN assert
    assert mongo_run == {'date': dt(2019, 3, 1, 0, 0), 'avg': {}, 'lanes': {}}
