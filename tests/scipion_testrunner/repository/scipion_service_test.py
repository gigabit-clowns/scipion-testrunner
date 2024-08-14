from unittest.mock import patch

import pytest

from scipion_testrunner.application.logger import logger
from scipion_testrunner.repository import scipion_service

__SCIPION = "scipion"
__MODULE = "mumodule"

def test_exists_with_error_when_test_search_fails(__mock_run_shell_command, __mock_print):
  error_text = "Test fail"
  __mock_run_shell_command.return_value = (1, error_text)
  with pytest.raises(SystemExit):
    scipion_service.get_all_tests(__SCIPION, __MODULE)
  __mock_print.assert_called_once_with(
    logger.red(f"{error_text}\nERROR: Test search command failed. Check line above for more detailed info."),
    flush=True
  )

@pytest.fixture
def __mock_run_shell_command():
  with patch("scipion_testrunner.repository.shell_service.run_shell_command") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_print():
  with patch("builtins.print") as mock_method:
    yield mock_method
