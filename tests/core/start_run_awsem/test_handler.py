import pytest
from core.start_run_awsf.service import (
    handler,
    get_format_extension_map,
    handle_processed_files,
    proc_file_for_arg_name,
)
from ..conftest import valid_env
from core.utils import Tibanna
from core import ff_utils
import mock


@valid_env
@pytest.mark.webtest
def test_start_awsem_handler(run_awsf_event_data):
    # data = service.handler(run_awsf_event_data, '')
    res = handler(run_awsf_event_data, '')
    assert(res)


@valid_env
@pytest.mark.webtest
def test_start_awsem_handler_processed_files(run_awsf_event_data_processed_files):
    res = handler(run_awsf_event_data_processed_files, '')
    assert(res)
    assert('pf_meta' in res)
    assert('source_experiments' in res['pf_meta'][0])


@pytest.fixture()
def proc_file_in_webdev():
    return {'status': 'released',
            'uuid': 'f6d5ba22-aaf9-48e9-8df4-bc5c131c96af',
            'file_format': 'normvector_juicerformat',
            'accession': '4DNFIRO3UX7I',
            'award': '/awards/1U01CA200059-01/',
            'lab': '/labs/4dn-dcic-lab/'}


@valid_env
@pytest.mark.webtest
def test_proc_file_for_arg_name(run_awsf_event_data_processed_files, proc_file_in_webdev):
    of = [{"workflow_argument_name": "output_file1",
           "uuid": proc_file_in_webdev['uuid']
           },
          {"workflow_argument_name": "output_file2",
           "uuid": "f4864029-a8ad-4bb8-93e7-5108f46bbbbb"
           }]

    tibanna_settings = run_awsf_event_data_processed_files.get('_tibanna', {})
    # if they don't pass in env guess it from output_bucket
    env = tibanna_settings.get('env')
    # tibanna provides access to keys based on env and stuff like that
    tibanna = Tibanna(env, s3_keys=run_awsf_event_data_processed_files.get('s3_keys'),
                      ff_keys=run_awsf_event_data_processed_files.get('ff_keys'),
                      settings=tibanna_settings)

    file_with_type = proc_file_in_webdev.copy()
    file_with_type['@type'] = ['FileProcessed', 'Item', 'whatever']
    with mock.patch('core.ff_utils.get_metadata', return_value=file_with_type):
        pf = proc_file_for_arg_name(of, 'output_file1', tibanna)
        assert type(pf) == ff_utils.ProcessedFileMetadata
        assert pf.__dict__ == proc_file_in_webdev


def test_psuedo_run(run_task_awsf_psuedo_workflow_event_data):
    res = handler(run_task_awsf_psuedo_workflow_event_data, '')
    assert(res)


@valid_env
@pytest.mark.webtest
def test_start_awsem_handle_processed_files2(run_awsf_event_data_processed_files2):
    res = handler(run_awsf_event_data_processed_files2, '')
    assert(res)
    assert('pf_meta' in res)
    assert('source_experiments' in res['pf_meta'][0])


@valid_env
@pytest.mark.webtest
def test_start_awsem_handler_secondary_files(run_awsf_event_data_secondary_files):
    try:
        handler(run_awsf_event_data_secondary_files, '')
    except Exception as e:
        print(e)
        pytest.skip("seems data is not in place")


@valid_env
@pytest.mark.webtest
def test_get_format_extension_map(run_awsf_event_data):
    tibanna_settings = run_awsf_event_data.get('_tibanna', {})
    # if they don't pass in env guess it from output_bucket
    env = tibanna_settings.get('env')
    # tibanna provides access to keys based on env and stuff like that
    tibanna = Tibanna(env, s3_keys=run_awsf_event_data.get('s3_keys'),
                      ff_keys=run_awsf_event_data.get('ff_keys'),
                      settings=tibanna_settings)

    fe_map = get_format_extension_map(tibanna)
    assert(fe_map)
    assert 'pairs' in fe_map.keys()


@valid_env
@pytest.mark.webtest
def test_handle_processed_files(run_awsf_event_data_secondary_files):
    data = run_awsf_event_data_secondary_files
    tibanna_settings = data.get('_tibanna', {})
    # if they don't pass in env guess it from output_bucket
    env = tibanna_settings.get('env')
    # tibanna provides access to keys based on env and stuff like that
    tibanna = Tibanna(env, s3_keys=data.get('s3_keys'),
                      ff_keys=data.get('ff_keys'),
                      settings=tibanna_settings)
    workflow_uuid = data['workflow_uuid']
    workflow_info = ff_utils.get_metadata(workflow_uuid, key=tibanna.ff_keys)

    output_files, pf_meta = handle_processed_files(workflow_info, tibanna)
    assert(output_files)
    assert len(output_files) == 3
    for of in output_files:
        if of['extension'] == '.pairs.gz':
            assert of['secondary_file_extensions'] == ['.pairs.gz.px2']
            assert of['secondary_file_formats'] == ['pairs_px2']
            assert of['extra_files']
        else:
            assert 'secondary_files_extension' not in of
            assert 'secondary_files_formats' not in of

    assert(pf_meta)
    assert len(pf_meta) == 3
    for pf in pf_meta:
        pdict = pf.__dict__
        if pdict['file_format'] == 'pairs':
            assert pdict['extra_files'] == [{'file_format': 'pairs_px2'}]
        else:
            assert 'extra_files' not in pdict
