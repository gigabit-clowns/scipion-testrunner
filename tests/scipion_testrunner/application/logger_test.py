from unittest.mock import patch
from io import BytesIO

import pytest

from scipion_testrunner.application.logger import Logger

__TEST_STRING = "Test print"
__LOG_FILE = BytesIO()

def test_opens_the_expected_file_when_starting_log_file(__mock_open):
  logger = Logger()
  logger.start_log_file(__TEST_STRING)
  __mock_open.assert_called_once_with(__TEST_STRING, "w")

def test_logger_is_called_with_expected_text_when_logging_to_stdout(__mock_print):
  logger = Logger()
  logger(__TEST_STRING)
  __mock_print.assert_called_once_with(__TEST_STRING, flush=True)
def test_logger_is_called_with_expected_text_when_logging_to_file(__mock_print, __mock_open):
  logger = Logger()
  logger.start_log_file("")
  logger(__TEST_STRING)
  __mock_print.assert_called_with(__TEST_STRING, flush=True, file=__LOG_FILE)

def test_logger_is_called_with_expected_text_when_logging_warning(__mock_print):
  logger = Logger()
  logger.log_warning(__TEST_STRING)
  __mock_print.assert_called_with(logger.yellow(__TEST_STRING), flush=True)

@pytest.fixture
def __mock_print():
  with patch("builtins.print") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_open():
  with patch("builtins.open") as mock_method:
    mock_method.return_value = __LOG_FILE
    yield mock_method