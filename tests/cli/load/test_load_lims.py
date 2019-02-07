
from vogue.commands.load.lims import lims
from vogue.server import create_app
from vogue.commands.base import cli
import pytest

app = create_app()



def test_lims(database):
    app.db = database

    ## GIVEN a lims sample ID
    sample_id = 'MIC3559A64'
    
    ## WHEN adding the sample
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['load', 'lims', '-s', sample_id])

    ## THEN assert the new sample should be added to the colleciton
    assert app.adapter.sample(sample_id)['_id'] == sample_id



def test_lims_wrong_input(database):
    app.db = database

    ## GIVEN a non existing lims  sample id
    sample_id = 'WRONGID'

    ## WHEN adding the sample
    ## THEN assert error
    runner = app.test_cli_runner()
    with pytest.raises(ValueError):
        result = runner.invoke(cli, ['load', 'lims', '-s', sample_id])
        #Not working" Need help!
