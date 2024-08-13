from unittest.mock import patch

import pytest

from scipion_testrunner.application import cli

def test_calls_required_parse_args_function(__mock_parse_args, __mock_test_service):
  cli.main()
  __mock_parse_args.assert_called_once()

def test_calls_required_test_service_function(__mock_parse_args, __mock_test_service):
  cli.main()
  __mock_test_service.assert_called_once()

@pytest.fixture
def __mock_parse_args():
  with patch("scipion_testrunner.application.cli.__get_args_from_parser") as mock_method:
    mock_method.return_value = {}
    yield mock_method

@pytest.fixture
def __mock_test_service():
  with patch("scipion_testrunner.domain.test_service.test_scipion_plugin") as mock_method:
    yield mock_method
