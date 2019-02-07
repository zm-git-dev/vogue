import pytest

import mongomock

DATABASE = 'testdb'

@pytest.fixture(scope='function')
def pymongo_client(request):
    """Get a client to the mongo database"""
    mock_client = mongomock.MongoClient()
    def teardown():
        mock_client.drop_database(DATABASE)
    request.addfinalizer(teardown)
    return mock_client

@pytest.fixture(scope='function')
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""
    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database