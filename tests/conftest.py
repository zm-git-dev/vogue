import pytest

from mongomock import MongoClient

from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
from genologics.lims import Lims
LIMS = Lims(BASEURI,USERNAME,PASSWORD)

#from vogue.load.lims import build_sample

DATABASE = 'vogue'


class MockProcess():
    def __init__(self, date_str = '2014-01-28'):
        self.date_run = date_str

class MockArtifact():
    def __init__(self):
        self.parent_process = MockProcess()

class MockLims():
    def __init__(self):
        self.artifacts = []
    
    def get_artifacts(self, process_type, samplelimsid)-> list:
        """"Get a list of artifacts."""
        return self.artifacts
    
    def _add_artifact(self, artifact):
        self.artifacts.append(artifact)

class MockSample():
    def __init__(self, sample_id='sample', lims=MockLims(), udfs={}):
        self.id = sample_id
        self.udf = udfs





@pytest.fixture
def lims():
    return MockLims()

@pytest.fixture
def lims_sample():
    return MockSample()

@pytest.fixture
def family_sample():
    return MockSample(udfs={'Family':'1'})

@pytest.fixture
def simple_artifact():
    return MockArtifact()

#@pytest.fixture
#def mongo_sample(lims_sample):
#    return build_sample(lims_sample)

#@pytest.fixture(scope='function')
#def pymongo_client(request):
#    """Get a client to the mongo database"""
#
#    logger.info("Get a mongomock client")
#    start_time = datetime.datetime.now()
#    mock_client = MongoClient()
#
#    def teardown():
#        mock_client.drop_database(DATABASE)
#
#    request.addfinalizer(teardown)
#
#    return mock_client