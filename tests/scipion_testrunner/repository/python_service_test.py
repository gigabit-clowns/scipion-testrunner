from typing import Callable, Optional
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
  "return_code,succeeded,message_fragment",
  [
    pytest.param(0, True, "did not suceed"),
    pytest.param(1, False, "succeeded")
  ]
)
def test_returns_expected_status_when_testing_python_command(return_code, succeeded, message_fragment, __mock_run_shell_command):
  __mock_run_shell_command.return_value = return_code, ""
  assert (
    python_service.python_command_succeeded("test-command") == succeeded
  ), f"Command {message_fragment}."

@pytest.mark.parametrize(
  "params,n_errors",
  [
    pytest.param([True, True], 0),
    pytest.param([False, True], 1),
    pytest.param([True, False], 1),
    pytest.param([False, False], 2)
  ]
)
def test_returns_expected_statuses_when_running_parallel_function(params, n_errors, __mock_pool_apply):
  assert (
    len(python_service.run_function_in_parallel(ExitState, parallelizable_params=params)) == n_errors
  ), "Parallel function call returned different number of errors than expected."

class ExitState:
  """
  ### Mock substitute for multiprocessing.pool.AsyncResult.
  """
  def __init__(self, success: bool):
    """
    ### Constructor

    #### Params:
    - success (bool): Success state of the faked operation.
    """
    self.success = success
  
  def get(self) -> Optional[str]:
    """
    ### Returns a message if the state of the fake operation is failure.

    #### Returns:
    - (str | None): Message if the sate is a failure.
    """
    if not self.success:
      return "Failed"

def __run_function_async(func: Callable, args):
  """
  ### Calls the received callable with given args.

  #### Params:
  - func (callable): Callable to run.
  - args (Any): Args to be passed on to the callable.

  #### Returns:
  - (Any): Output of the callable.
  """
  all_params = [*args]
  return func(args[0], *all_params[1:])

@pytest.fixture
def __mock_python_command_succeeded():
  with patch("scipion_testrunner.repository.python_service.python_command_succeeded") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_run_shell_command():
  with patch("scipion_testrunner.repository.shell_service.run_shell_command") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_pool_apply():
  with patch("multiprocessing.pool.Pool.apply_async") as mock_method:
    mock_method.side_effect = __run_function_async
    yield mock_method
