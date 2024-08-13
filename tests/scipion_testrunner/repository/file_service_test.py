import json
import os
from io import BytesIO
from unittest.mock import patch

import pytest

from scipion_testrunner.repository import file_service

__DATASETS_KEY = "datasets"
__SKIPPABLE_KEY = "skippable"
__TEST_DEPENDENCIES_KEY = "test-dependencies"
__DUMMY_FILE_PATH = "path"
__FILE_DATA = {
  __DATASETS_KEY: ['1', '2'],
  "skippable": {'key': 'value'},
  "test-dependencies": {'key': 'value'}
}
__LOG_FILE = BytesIO(json.dumps(__FILE_DATA).encode())

def test_returns_empty_fields(__mock_log):
  assert (
    file_service.read_test_data_file("") == [], {}, {}
  ), "Empty file path should have returned empty fields."

def test_returns_expected_fields(__mock_open):
  assert (
    file_service.read_test_data_file(__DUMMY_FILE_PATH) == (
      __FILE_DATA[__DATASETS_KEY],
      __FILE_DATA[__SKIPPABLE_KEY],
      __FILE_DATA[__TEST_DEPENDENCIES_KEY]
    )
  ), "Test data file did not return the expected data."

def test_exits_on_file_not_found_error(__mock_open_raise_file_not_found_error, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)

def test_exits_on_is_a_directory_error(__mock_open_raise_is_directory_error, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)

def test_exits_on_permission_error(__mock_open_raise_permission_error, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)

def test_exits_on_json_decode_error(__mock_open, __mock_json_load_raise_exception, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)

def test_exits_on_exception(__mock_open_raise_exception, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)

@pytest.fixture
def __mock_log():
  with patch("scipion_testrunner.application.logger.Logger.__call__") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_open():
  with patch("builtins.open") as mock_method:
    mock_method.return_value = __LOG_FILE
    yield mock_method

@pytest.fixture
def __mock_open_raise_file_not_found_error(__mock_open):
  __mock_open.side_effect = FileNotFoundError()

@pytest.fixture
def __mock_open_raise_is_directory_error(__mock_open):
  __mock_open.side_effect = IsADirectoryError()

@pytest.fixture
def __mock_open_raise_permission_error(__mock_open):
  __mock_open.side_effect = PermissionError()

@pytest.fixture
def __mock_json_load_raise_exception():
  with patch("json.load") as mock_method:
    mock_method.side_effect = json.JSONDecodeError("", "", 0)
    yield mock_method

@pytest.fixture
def __mock_open_raise_exception(__mock_open):
  __mock_open.side_effect = Exception()
