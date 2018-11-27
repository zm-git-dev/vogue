import pytest

from mongomock import MongoClient

from vogue.build.lims import build_sample
from vogue.adapter import VogueAdapter

from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
from genologics.lims import Lims

DATABASE = 'vogue'


class MockProcess():
    def __init__(self, date_str = '2018-01-01', process_type = None):
        self.date_run = date_str
        self.type = process_type
    
    def __repr__(self):
        return f"Process:date_run={self.date_run},type={self.type}"


class MockArtifact():
    def __init__(self, parent_process = None, samples = None):
        self.parent_process = parent_process
        self.samples = samples
        self.input_list = []

    def input_artifact_list(self):
        return self.input_list

    def __repr__(self):
        return f"Artifact:parent_process={self.parent_process},samples={self.samples}"



class MockLims():
    def __init__(self):
        self.artifacts = []
        self.processes = []
        self.samples = []
    
    def get_artifacts(self, process_type, samplelimsid)-> list:
        """"Get a list of artifacts."""
        arts = self.artifacts
        if process_type:
            arts = []
            for art in self.artifacts:
                if art.parent_process and art.parent_process.type in process_type:
                    arts.append(art)
        return arts
    
    def _add_artifact(self, parent_process = None, samples = []):
        artifact = MockArtifact(parent_process, samples)
        self.artifacts.append(artifact)
        return artifact

    def _add_process(self, date_str = None, process_type = None):
        process = MockProcess(date_str, process_type)
        self.processes.append(process)
        return process

    def _add_sample(self,sample_id):
        sample = MockSample(sample_id = sample_id)
        self.samples.append(sample)
        return sample




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
    return MockSample(udfs={'Family': '1'})


@pytest.fixture
def simple_artifact():
    return MockArtifact()


#@pytest.fixture
#def mongo_sample(lims_sample, lims):
#    return build_sample(lims_sample, lims)


@pytest.fixture
def test_sample():
    return {'_id': '1'}

@pytest.fixture
def sample_id(test_sample):
    return test_sample['_id']

@pytest.fixture
def cancer_analysis():
    return {'case_id': '1',
            'samples': ['1', '2'],
            'picard_markdup': ['path_file_sample_1', 'path_file_sample_2'],
            'TMB': 15,
            'workflow_name': 'BALSAMIC',
            'version_version': '2.7.1'}


@pytest.fixture(scope='function')
def pymongo_client(request):
    """Get a client to the mongo database"""

    mock_client = MongoClient()

    def teardown():
        mock_client.drop_database(DATABASE)

    request.addfinalizer(teardown)

    return mock_client


@pytest.fixture(scope='function')
def adapter(request, pymongo_client):
    """Get a client to the mongo database"""
    return VogueAdapter(pymongo_client, DATABASE)
