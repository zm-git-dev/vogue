import pytest

from mongomock import MongoClient

from vogue.adapter import VougeAdapter

from genologics.entities import Sample
from genologics.config import BASEURI, USERNAME, PASSWORD
from genologics.lims import Lims

DATABASE = 'testdb'

import logging
LOG = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def pymongo_client(request):
    """Get a client to the mongo database"""
    mock_client = MongoClient()

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


class MockProcess():
    def __init__(self,
                 date_str='2018-01-01',
                 process_type=None,
                 pid=None,
                 modified=None,
                 input_output_maps=[]):
        self.date_run = date_str
        self.type = process_type
        self.udf = {}
        self.input_artifact_list = []
        self.id = pid
        self.outputs = []
        self.inputs = []
        self.input_output_maps = input_output_maps
        self.modified = modified

    def all_outputs(self):
        return self.outputs

    def all_inputs(self):
        return self.inputs

    def __repr__(self):
        return f"Process:date_run={self.date_run},type={self.type}"


class MockProcessType():
    def __init__(self, name=''):
        self.name = name

    def __repr__(self):
        return f"ProcessType:name={self.name}"


class MockContainerType():
    def __init__(self, name=''):
        self.name = name

    def __repr__(self):
        return f"ProcessType:name={self.name}"


class MockContainer():
    def __init__(self, name='', type=MockContainerType()):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"ProcessType:name={self.name}"


class MockArtifact():
    def __init__(self,
                 parent_process=None,
                 samples=None,
                 id=None,
                 location=(),
                 udf={},
                 qc_flag='UNKNOWN',
                 reagent_labels=[],
                 type=None):
        self.id = id
        self.location = location
        self.parent_process = parent_process
        self.samples = samples
        self.input_list = []
        self.udf = udf
        self.qc_flag = qc_flag
        self.reagent_labels = reagent_labels
        self.type = type

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

    def get_samples(self) -> list:
        return self.samples

    def get_artifacts(self, process_type, samplelimsid) -> list:
        """"Get a list of artifacts."""
        if not isinstance(process_type, list):
            process_type = [process_type]
        arts = []
        for art in self.artifacts:
            if process_type:
                if not art.parent_process:
                    continue
                elif not art.parent_process.type.name in process_type:
                    continue
            if samplelimsid:
                if not samplelimsid in [s.id for s in art.samples]:
                    continue
            arts.append(art)
        return arts

    def get_processes(self,
                      type=None,
                      udf={},
                      inputartifactlimsid=None,
                      last_modified=None):
        processes = []
        for process in self.processes:
            if isinstance(type, list) and (process.type.name not in type):
                continue
            elif isinstance(type, str) and (process.type.name != type):
                continue
            if udf:
                subset = {key: process.udf.get(key) for key in udf}
                if subset != udf:
                    continue
            if inputartifactlimsid:
                if inputartifactlimsid not in [
                        a.id for a in process.input_artifact_list
                ]:
                    continue
            if last_modified:
                LOG.info(process.modified)
                if last_modified > process.modified:
                    continue
            processes.append(process)
        LOG.info(str(processes))
        return processes

    def _add_artifact(self, parent_process=None, samples=[], id=None, udf={}):
        artifact = MockArtifact(parent_process=parent_process,
                                samples=samples,
                                id=id,
                                udf=udf)
        self.artifacts.append(artifact)
        return artifact

    def _add_process_type(self, name=''):
        process_type = MockProcessType(name)
        self.process_types.append(process_type)
        return process_type

    def _add_process(self, date_str=None, process_type=None, pid=None):
        process = MockProcess(date_str, process_type, pid=pid)
        self.processes.append(process)
        return process

    def _add_sample(self, sample_id):
        sample = MockSample(sample_id=sample_id)
        self.samples.append(sample)
        return sample

    def __repr__(self):
        return (f"Lims:artifacts={self.artifacts},process={self.processes},"
                "process_types={self.process_types},samples={self.samples}")


class MockSample():
    def __init__(self,
                 sample_id='sample',
                 lims=MockLims(),
                 udfs={},
                 artifact=MockArtifact()):
        self.id = sample_id
        self.udf = udfs
        self.artifact = artifact

    def __repr__(self):
        return f"Sample:id={self.id},udf={self.udf}"


class MockReagentLabel():
    def __init__(self,
                 name='IDT_10nt_NXT_109',
                 sequence='TAGGAAGCGG-CCTGGATTGG',
                 category='Illumina IDT'):
        self.name = name
        self.sequence = sequence
        self.category = category

    def __repr__(self):
        return f"ReagentLabel:name={self.name},category={self.category}"


@pytest.fixture
def lims_reagent_label():
    return MockReagentLabel()


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


@pytest.fixture
def run():
    run = MockProcess(date_str='2018-01-01',
                      process_type='AUTOMATED - NovaSeq Run',
                      pid='24-100451')
    return MockProcess()


@pytest.fixture(scope='function')
def build_bcl_step():
    def create(index='A07-UDI0049',
               bcl_step_id='24-100451',
               flowcell_id='hej',
               index_target_reads='25',
               index_total_reads=[{
                   1: {
                       '# Reads': 5000000
                   },
                   2: {
                       '# Reads': 5000000
                   },
                   3: {
                       '# Reads': 5000000
                   },
                   4: {
                       '# Reads': 5000000
                   }
               }],
               sample='ACC6457A1',
               flowcell_type='S4',
               define_step_udfs={}):
        sample = MockSample(sample_id='ACC6457A1',
                            udfs={'Sequencing Analysis': 'ABC'})

        define = MockProcessType(
            name='Define Run Format and Calculate Volumes (Nova Seq)')
        define_process = MockProcess(process_type=define)
        define_art = MockArtifact(
            udf={'Reads to sequence (M)': index_target_reads},
            samples=[sample],
            reagent_labels=[index],
            id='define_output',
            type='Analyte',
            parent_process=define_process)
        define_process.outputs = [define_art]

        prepare = MockProcessType(
            name='STANDARD Prepare for Sequencing (Nova Seq)')
        prepare_process = MockProcess(process_type=prepare)
        prepare_process.inputs = [define_art]

        input_output_maps = []
        for nr, index_reads in index_total_reads.items():
            bcl_art = MockArtifact(udf=index_reads,
                                   qc_flag='PASSED',
                                   samples=[sample],
                                   reagent_labels=[index],
                                   id='bcl_output')
            lane = MockArtifact(location=(MockContainer(name=flowcell_id), nr),
                                samples=[sample],
                                parent_process=prepare_process,
                                id='prepare_output')
            prepare_process.outputs.append(lane)
            input_output_maps.append(({
                'uri': lane,
                'parent-process': prepare_process
            }, {
                'uri':
                bcl_art,
                'output-generation-type':
                'PerReagentLabel'
            }))

        bcl_process = MockProcess(pid=bcl_step_id,
                                  input_output_maps=input_output_maps)

        return bcl_process

    return create


@pytest.fixture
def test_sample():
    return {'_id': '1'}


@pytest.fixture
def sample_id(test_sample):
    return test_sample['_id']


@pytest.fixture
def cancer_analysis():
    return {
        'case_id': '1',
        'samples': ['1', '2'],
        'picard_markdup': ['path_file_sample_1', 'path_file_sample_2'],
        'TMB': 15,
        'workflow_name': 'BALSAMIC',
        'version_version': '2.7.1'
    }


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
    return VougeAdapter(pymongo_client, DATABASE)


##########################################
###### fixture files for input json ######
##########################################


@pytest.fixture
def get_valid_json():
    """Get file path to valid json"""
    json_path = 'tests/fixtures/valid_multiqc.json'
    return json_path


@pytest.fixture
def get_invalid_json():
    """Get file path to invalid json"""
    json_path = 'tests/fixtures/not_a_multiqc_report.json'
    return json_path
