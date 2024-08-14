import json
from unittest.mock import patch

import pytest

from scipion_testrunner.application.logger import logger
from scipion_testrunner.repository import file_service

__DATASETS_KEY = "datasets"
__SKIPPABLE_KEY = "skippable"
__TEST_DEPENDENCIES_KEY = "test-dependencies"
__DUMMY_FILE_PATH = "path"
__FILE_DATA = {
  __DATASETS_KEY: ['1', '2'],
  __SKIPPABLE_KEY: {'key': 'value'},
  __TEST_DEPENDENCIES_KEY: {'key': 'value'}
}
__EXCEPTION_TEXT = "Test"
__JSON_EXCEPTION = json.JSONDecodeError(__EXCEPTION_TEXT, __DUMMY_FILE_PATH, 1)

def test_returns_empty_fields(__mock_log):
  assert (
    file_service.read_test_data_file("") == ([], {}, {})
  ), "Empty file path should have returned empty fields."

def test_returns_expected_fields(__mock_open, __mock_json_load):
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
  __mock_log.assert_called_once_with(logger.red(f"ERROR: File '{__DUMMY_FILE_PATH}' does not exist."))

def test_exits_on_is_a_directory_error(__mock_open_raise_is_directory_error, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)
  __mock_log.assert_called_once_with(logger.red(f"ERROR: Path '{__DUMMY_FILE_PATH}' provided is a directory."))

def test_exits_on_permission_error(__mock_open_raise_permission_error, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)
  __mock_log.assert_called_once_with(logger.red(f"ERROR: Permission denied to open file '{__DUMMY_FILE_PATH}'."))

def test_exits_on_json_decode_error(__mock_open, __mock_json_load_raise_json_decode_error, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)
  __mock_log.assert_called_once_with(
    logger.red(f"ERROR: Invalid JSON format in file '{__DUMMY_FILE_PATH}':\n{__JSON_EXCEPTION}")
  )

def test_exits_on_exception(__mock_open_raise_exception, __mock_log):
  with pytest.raises(SystemExit):
    file_service.read_test_data_file(__DUMMY_FILE_PATH)
  __mock_log.assert_called_once_with(logger.red(f"An unexpected error occurred:\n{__EXCEPTION_TEXT}"))

@pytest.fixture
def __mock_log():
  with patch("scipion_testrunner.application.logger.Logger.__call__") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_open():
  with patch("builtins.open") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_json_load():
  with patch("json.load") as mock_method:
    mock_method.return_value = __FILE_DATA
    yield mock_method

@pytest.fixture
def __mock_open_raise_file_not_found_error(__mock_open):
  __mock_open.side_effect = FileNotFoundError(__EXCEPTION_TEXT)

@pytest.fixture
def __mock_open_raise_is_directory_error(__mock_open):
  __mock_open.side_effect = IsADirectoryError(__EXCEPTION_TEXT)

@pytest.fixture
def __mock_open_raise_permission_error(__mock_open):
  __mock_open.side_effect = PermissionError(__EXCEPTION_TEXT)

@pytest.fixture
def __mock_json_load_raise_json_decode_error(__mock_json_load):
  __mock_json_load.side_effect = __JSON_EXCEPTION

@pytest.fixture
def __mock_open_raise_exception(__mock_open):
  __mock_open.side_effect = Exception(__EXCEPTION_TEXT)
