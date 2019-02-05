from functools import partial

from click.testing import CliRunner
import pytest

from vogue.commands import base
DATABASE = 'testdb'
import mongomock


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner
    

@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, base)

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