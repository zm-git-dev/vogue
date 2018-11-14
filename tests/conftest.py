import pytest

from mongomock import MongoClient

from vogue.build.lims import build_sample
from vogue.adapter import VogueAdapter

DATABASE = 'vogue'


class MockProcess():
    def __init__(self, date_str='2014-01-28'):
        self.date_run = date_str


class MockArtifact():
    def __init__(self):
        self.parent_process = MockProcess()


class MockLims():
    def __init__(self):
        self.artifacts = []

    def get_artifacts(self, process_type, samplelimsid) -> list:
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
    return {'sample_id': '1',
            'dup_rate': 0.1,
            'somtatic_var_callers': ['VARDICT','MUTECT2','STRELKA','MANTA'],
            'sample_type': 'tumor',
            'analysis_type': 'paired',
            'somatic_var_count': [9870,765,123,456],
            'var_type': ['SNV_INDEL','SNV_INDEL','SNV_INDEL', 'SV'],
            'TMB': 15,
            'biopsy_type': 'FFPE',
            'fixation_time_hour': 24,
            'total_passed_read': 12345678,
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
