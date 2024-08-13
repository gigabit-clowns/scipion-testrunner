from unittest.mock import patch

import pytest

from scipion_testrunner.repository import python_service

__MODULE_NAME = "test"

@pytest.mark.parametrize(
  "exists,message_fragment",
  [
    pytest.param(True, "does not exist"),
    pytest.param(False, "exists")
  ]
)
def test_returns_expected_value_when_checking_if_module_exists(exists, message_fragment, __mock_python_command_succeeded):
  __mock_python_command_succeeded.return_value = exists
  assert (
    python_service.exists_python_module(__MODULE_NAME) == exists
  ), f"Function returns that module {message_fragment}."

@pytest.mark.parametrize(
  "return_code,suceeded,message_fragment",
  [
    pytest.param(0, True, "did not suceed"),
    pytest.param(1, False, "suceeded")
  ]
)
def test_returns_expected_status_when_testing_python_command(return_code, suceeded, message_fragment, __mock_run_shell_command):
  __mock_run_shell_command.return_value = return_code, ""
  assert (
    python_service.python_command_succeeded("test-command") == suceeded
  ), f"Command {message_fragment}."

@pytest.fixture
def __mock_python_command_succeeded():
  with patch("scipion_testrunner.repository.python_service.python_command_succeeded") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_run_shell_command():
  with patch("scipion_testrunner.repository.shell_service.run_shell_command") as mock_method:
    yield mock_method
