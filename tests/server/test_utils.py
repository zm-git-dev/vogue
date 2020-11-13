from vogue.server import create_app
from vogue.server.utils import find_concentration_defrosts, find_concentration_amount, value_per_month, instrument_info
from vogue.adapter.plugin import VougeAdapter
from datetime import datetime

app = create_app(test=True)


def test_find_concentration_amount(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    year = 2018

    # GIVEN a database  with a sample document:
    sample = {
        "_id": "ACC2692A1",
        "amount": 322.5,
        "amount-concentration": 11.5,
        "received_date": datetime(year, 12, 1, 0, 0),
        "received_to_delivered": 22
    }

    database.sample.insert_one(sample)

    # WHEN running find_concentration_amount
    results = find_concentration_amount(app.adapter, year)

    # THEN assert the results should be equal to expected_result:
    expected_result = [{'x': 200, 'y': 11.5, 'name': 'ACC2692A1'}]
    assert results['data'] == expected_result


def test_find_concentration_defrosts(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    year = 2018

    # GIVEN a database  with a sample document:
    sample = {
        "_id": "ACC2559A1",
        "nr_defrosts": 2,
        "nr_defrosts-concentration": 5.71,
        "lotnr": "20124806",
        "received_date": datetime(year, 12, 1, 0, 0),
        "received_to_delivered": 13
    }
    database.sample.insert_one(sample)

    # WHEN running find_concentration_defrosts
    results = find_concentration_defrosts(app.adapter, year)

    # THEN assert the results should be equal to expected_result:
    expected_result = {
        '20124806': {
            'median': [[2, 5.71]],
            'nr_samples': [[2, 1]],
            'quartile': [[2, 5.71, 5.71]]
        }
    }
    assert results['data'] == expected_result


def test_count_value_per_month(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    year = 2018
    y_val = 'count'
    group_key = 'source'

    # GIVEN a database  with two sample documents:
    sample = {
        "_id": "test1",
        "source": "blood",
        "library_size_post_hyb": 333,
        "received_date": datetime(year, 12, 1, 0, 0),
        "received_to_delivered": 32
    }
    database.sample.insert_one(sample)
    sample = {
        "_id": "test2",
        "source": "blood",
        "library_size_post_hyb": 417,
        "received_date": datetime(year, 12, 1, 0, 0),
        "received_to_delivered": 32
    }
    database.sample.insert_one(sample)

    # WHEN running value_per_month:
    results = value_per_month(app.adapter, year, y_val, group_key)

    # THEN assert the results should be equal to expected_result:
    expected_result = {
        'blood': {
            'data': [
                None, None, None, None, None, None, None, None, None, None,
                None, 2
            ]
        }
    }
    assert results == expected_result


def test_y_val_value_per_month(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    year = 2018
    y_val = 'library_size_post_hyb'
    group_key = 'source'

    # GIVEN a database  with two sample documents:
    sample = {
        "_id": "test1",
        "source": "blood",
        "library_size_post_hyb": 333,
        "received_date": datetime(year, 12, 1, 0, 0),
        "received_to_delivered": 32
    }
    database.sample.insert_one(sample)
    sample = {
        "_id": "test2",
        "source": "blood",
        "library_size_post_hyb": 417,
        "received_date": datetime(year, 12, 1, 0, 0),
        "received_to_delivered": 32
    }
    database.sample.insert_one(sample)

    # WHEN running value_per_month:
    results = value_per_month(app.adapter, year, y_val, group_key)

    # THEN assert the results should be equal to expected_result:
    expected_result = {
        'blood': {
            'data': [
                None, None, None, None, None, None, None, None, None, None,
                None, 375.0
            ]
        }
    }
    assert results == expected_result


def test_q30_instruments(database):
    app.db = database
    app.adapter = VougeAdapter(database.client, db_name=database.name)
    year = 2017
    instrument = 'Marie'

    ## GIVEN a database  with two flowcell documents with instrument Marie:
    metric = "% Bases >=Q30"
    run1 = {
        "_id": "170530_ST-E00214_0154_AHJCL5ALXX",
        "instrument": instrument,
        "date": datetime(year, 5, 30, 0, 0),
        "avg": {
            metric: 90
        }
    }
    database.flowcell.insert_one(run1)

    run2 = {
        "_id": '171012_ST-E00214_0186_BHCGCKCCXY',
        "instrument": instrument,
        "date": datetime(year, 10, 12, 0, 0),
        "avg": {
            metric: 80
        }
    }
    database.flowcell.insert_one(run2)

    ## WHEN running find_concentration_amount
    results = instrument_info(app.adapter, year, metric)

    ## THEN assert the results for Marie should be as expected:
    expected = [[
        datetime(2017, 5, 30, 0, 0), 90, '170530_ST-E00214_0154_AHJCL5ALXX'
    ], [datetime(2017, 10, 12, 0, 0), 80, '171012_ST-E00214_0186_BHCGCKCCXY']]
    assert results['data'][metric][instrument]['data'] == expected
