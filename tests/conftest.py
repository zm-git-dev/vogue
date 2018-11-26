import pytest

from mongomock import MongoClient

from genologics.entities import Sample
from genologics.config import BASEURI,USERNAME,PASSWORD
from genologics.lims import Lims

#from vogue.load.lims import build_sample

DATABASE = 'vogue'


class MockProcess():
    def __init__(self, date_str = '2018-01-01', process_type = None, pid = None):
        self.date_run = date_str
        self.type = process_type
        self.udf = {}
        self.input_artifact_list = []
        self.id = pid
    
    def __repr__(self):
        return f"Process:date_run={self.date_run},type={self.type}"

class MockProcessType():
    def __init__(self, name = ''):
        self.name = name

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
        if not type(process_type)==list:
            process_type=[process_type]
        arts = self.artifacts
        if process_type:
            arts = []
            for art in self.artifacts:
                if art.parent_process and art.parent_process.type.name in process_type:
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