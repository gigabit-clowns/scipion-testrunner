import multiprocessing
import os
import sys
from unittest.mock import patch

import pytest

from scipion_testrunner.application import cli

__SCIPION = '/path/to/scipion'
__PLUGIN = 'myplugin'
__ARGS = ['', __SCIPION, __PLUGIN]
__ARGS_DICT = {
  'scipion': __SCIPION,
  'plugin': __PLUGIN,
  'jobs': multiprocessing.cpu_count(),
  'noGpu': False,
  'testData': ''
}

def test_calls_required_parse_args_function(__mock_parse_args, __mock_test_service):
  cli.main()
  __mock_parse_args.assert_called_once()

def test_calls_required_test_service_function(__mock_parse_args, __mock_test_service):
  cli.main()
  __mock_test_service.assert_called_once()

@pytest.mark.parametrize(
  "param_name,value",
  [
    pytest.param('jobs', 2),
    pytest.param('testData', os.path.abspath('/path/to/testData.json'))
  ]
)
def test_generates_expected_args(param_name, value, __mock_test_service):
  args = __ARGS_DICT.copy()
  args[param_name] = value
  with patch.object(sys, 'argv', [*__ARGS, f"--{param_name}", f"{value}"]):
    cli.main()
    __mock_test_service.assert_called_once_with(args)

def test_generates_expected_no_gpu_arg(__mock_test_service):
  args = __ARGS_DICT.copy()
  args['noGpu'] = True
  with patch.object(sys, 'argv', [*__ARGS, "--noGpu"]):
    cli.main()
    __mock_test_service.assert_called_once_with(args)

@pytest.mark.parametrize(
  "input_args",
  [
    pytest.param([]),
    pytest.param(['']),
    pytest.param(['', 'scipion'])
  ]
)
def test_returns_error_when_not_providing_required_params(input_args, __mock_test_service):
  with patch.object(sys, 'argv', input_args):
    with pytest.raises(SystemExit):
      cli.main()

@pytest.fixture
def __mock_parse_args():
  with patch("scipion_testrunner.application.cli.__get_args_from_parser") as mock_method:
    mock_method.return_value = {}
    yield mock_method

@pytest.fixture
def __mock_test_service():
  with patch("scipion_testrunner.domain.test_service.test_scipion_plugin") as mock_method:
    yield mock_method
