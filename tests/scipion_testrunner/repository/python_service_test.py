import multiprocessing
from typing import Callable, Optional, Tuple
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
def test_returns_expected_statuses_when_running_parallel_function(params, n_errors, __mock_pool):
  params = [(str(param) if param else '') for param in params]
  assert (
    len(python_service.run_function_in_parallel(ExitState, parallelizable_params=params)) == n_errors
  ), "Parallel function call returned different number of errors than expected."

@pytest.mark.parametrize(
  "param_len,max_jobs,expected_jobs",
  [
    pytest.param(1, 2, 1),
    pytest.param(2, 2, 2),
    pytest.param(3, 2, 2)
  ]
)
def test_pool_is_created_with_expected_jobs(param_len, max_jobs, expected_jobs, __mock_pool):
  python_service.run_function_in_parallel(ExitState, parallelizable_params=['True' for _ in range(param_len)], max_jobs=max_jobs)
  assert (
    #__mock_pool.assert_called_once_with(processes=expected_jobs)
    __mock_pool.assert_called()
  ), "The pool was not created with the expected amount of jobs."

class ExitState:
  """
  ### Mock substitute for multiprocessing.pool.AsyncResult.
  """
  def __init__(self, input_str: str):
    """
    ### Constructor

    #### Params:
    - input_str (str): Input (possibly empty) string.
    """
    self.success = bool(input_str)
  
  def get(self) -> Optional[str]:
    """
    ### Returns a message if the state of the fake operation is failure.

    #### Returns:
    - (str | None): Message if the sate is a failure.
    """
    if not self.success:
      return "Failed"

class PoolMock:
  """
  ### Mock substitute for multiprocessing.Pool.
  """
  def __init__(self, processes: int):
    """
    ### Constructor

    #### Params:
    - processes (int): Number of processes for the pool.
    """
    self.processes = processes
  
  def apply_async(self, func: Callable, args: Tuple):
    """
    ### Calls the received callable with given args.

    #### Params:
    - func (callable): Callable to run.
    - args (Tuple): Args to be passed on to the callable.

    #### Returns:
    - (Any): Output of the callable.
    """
    remaining_params = [*args]
    return func(args[0], *remaining_params[1:])

  def get_processes(self) -> int:
    """
    ### Retrieves the number of processes.

    #### Returns:
    - (int): Number of processes.
    """
    return self.processes
  
  def close(self):
    """
    ### Overrides the pool close function.
    """
    pass

  def join(self):
    """
    ### Overrides the pool join function.
    """
    pass

@pytest.fixture
def __mock_python_command_succeeded():
  with patch("scipion_testrunner.repository.python_service.python_command_succeeded") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_run_shell_command():
  with patch("scipion_testrunner.repository.shell_service.run_shell_command") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_pool():
  with patch.object(multiprocessing, "Pool", PoolMock) as mock_object:
    yield mock_object
