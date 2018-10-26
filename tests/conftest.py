import pytest

from mongomock import MongoClient

from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
from genologics.lims import Lims
LIMS = Lims(BASEURI,USERNAME,PASSWORD)

from vogue.load.lims import build_sample

DATABASE = 'vogue'

class MockSample():
    def __init__(self, sample_id='sample', lims=LIMS, udfs={}):
        self.id = sample_id
        self.udf = udfs

@pytest.fixture
def lims_sample():
    return MockSample()

@pytest.fixture
def family_sample():
    return MockSample(udfs={'Family':'1'})

@pytest.fixture
def mongo_sample(lims_sample):
    return build_sample(lims_sample)

@pytest.fixture(scope='function')
def pymongo_client(request):
    """Get a client to the mongo database"""

    logger.info("Get a mongomock client")
    start_time = datetime.datetime.now()
    mock_client = MongoClient()

    def teardown():
        mock_client.drop_database(DATABASE)

    request.addfinalizer(teardown)

    return mock_client