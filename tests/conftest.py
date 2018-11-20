import pytest

from mongomock import MongoClient

from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
from genologics.lims import Lims
LIMS = Lims(BASEURI,USERNAME,PASSWORD)

#from vogue.load.lims import build_sample

DATABASE = 'vogue'


class MockProcess():
    def __init__(self, date_str = None, process_type = None):
        self.date_run = date_str
        self.type = process_type

class MockArtifact():
    def __init__(self, parent_process = None):
        self.parent_process = parent_process


class MockLims():
    def __init__(self):
        self.artifacts = []
        self.processes = []
    
    def get_artifacts(self, process_type, samplelimsid)-> list:
        """"Get a list of artifacts."""
        return self.artifacts
    
    def _add_artifact(self, parent_process = None):
        artifact = MockArtifact(parent_process)
        self.artifacts.append(artifact)
        return artifact

    def _add_process(self, date_str = None, process_type = None):
        process = MockProcess(date_str, process_type)
        self.processes.append(process)
        return process


class MockSample():
    def __init__(self, sample_id='sample', lims=MockLims(), udfs={}):
        self.id = sample_id
        self.udf = udfs



@pytest.fixture
def artifacts_with_different_dates():
    return MockArtifact()

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