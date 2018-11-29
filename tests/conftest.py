import pytest

from mongomock import MongoClient

from vogue.build.lims import build_sample
from vogue.adapter import VogueAdapter

from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
from genologics.lims import Lims

DATABASE = 'vogue'


class MockProcess():
    def __init__(self, date_str = '2018-01-01', process_type = None, pid = None):
        self.date_run = date_str
        self.type = MockProcessType(process_type)
        self.udf = {}
        self.input_artifact_list = []
        self.id = pid
    
    def __repr__(self):
        return f"Process:date_run={self.date_run},type={self.type}"

class MockProcessType():
    def __init__(self, name = ''):
        self.name = name

    def __repr__(self):
        return f"ProcessType:name={self.name}"

class MockArtifact():
    def __init__(self, parent_process = None, samples = None, id=None):
        self.id = id
        self.parent_process = parent_process
        self.samples = samples
        self.input_list = []
        self.udf = {}

    def input_artifact_list(self):
        return self.input_list

    def __repr__(self):
        return f"Artifact:parent_process={self.parent_process},samples={self.samples}"


class MockLims():
    def __init__(self):
        self.artifacts = []
        self.processes = []
        self.process_types = []
        self.samples = []
    
    def get_artifacts(self, process_type, samplelimsid)-> list:
        """"Get a list of artifacts."""
        if not isinstance(process_type,list):
            process_type=[process_type]
        arts = []
        for art in self.artifacts:
            ok = True
            if process_type:
                print('hej')
                if not art.parent_process:
                    ok = False
                    print('du')
                elif not art.parent_process.type.name in process_type:
                    ok = False
                    print('glade')
                    
            if samplelimsid:
                if not samplelimsid in [s.id for s in art.samples]:
                    ok = False
                    print('köp')
                    
            if ok:
                print('dig')
                arts.append(art)

        return arts


    def get_processes(self, type = None, udf = {}, inputartifactlimsid=None): 
        processes = []
        
        for process in self.processes:
            ok = True
            if type and process.type.name != type:
                ok = False
            if udf:
                for key, val in udf.items():
                    if not process.udf.get(key) or process.udf.get(key)!=val:
                        ok = False
            if inputartifactlimsid:
                if inputartifactlimsid not in [a.id for a in process.input_artifact_list]:
                    ok = False
            if ok:
               processes.append(process)
            

        return  processes

    
    def _add_artifact(self, parent_process = None, samples = [], id=None):
        artifact = MockArtifact(parent_process, samples, id)
        self.artifacts.append(artifact)
        return artifact

    def _add_process_type(self, name = ''):
        process_type = MockProcessType(name)
        self.process_types.append(process_type)
        return process_type

    def _add_process(self, date_str = None, process_type = None, pid = None):
        process = MockProcess(date_str, process_type, pid = pid)
        self.processes.append(process)
        return process

    def _add_sample(self,sample_id):
        sample = MockSample(sample_id = sample_id)
        self.samples.append(sample)
        return sample
    
    def __repr__(self):
        return (f"Lims:artifacts={self.artifacts},process={self.processes},"
                "process_types={self.process_types},samples={self.samples}")


class MockSample():
    def __init__(self, sample_id='sample', udfs={}):
        self.id = sample_id
        self.udf = udfs

    def __repr__(self):
        return f"Sample:id={self.id},udf={self.udf}"


@pytest.fixture
def lims():
    return MockLims()


@pytest.fixture
def lims_sample():
    return MockSample()

@pytest.fixture
def dummy_sample():
    return MockSample(sample_id='Dummy')


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
