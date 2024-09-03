from unittest.mock import patch, call, Mock

import pytest

from scipion_testrunner.application.logger import logger
from scipion_testrunner.domain.handlers import scipion_handler

__SCIPION = "scipion"
__MODULE = "mymodule"
__TEST_LIST_STRING = f"""
TEST: Scipion v3.6.0 - Eugenius

 >>> WARNING: XmippImage library not found!
  > Please install Xmipp to get full functionality for cryo electron microscopy workflows. Otherwise ignore this.
(Configuration->Plugins->scipion-em-xmipp -> expand, in Scipion plugin manager window)


Set SCIPION_CANCEL_XMIPP_BINDING_WARNING = True to cancel this message.

Scanning tests...
 scipion3 tests {__MODULE}.tests.workflows.test_workflow_xmipp_rct
   scipion3 tests {__MODULE}.tests.workflows.test_workflow_xmipp_rct.TestXmippRCTWorkflow
 scipion3 tests {__MODULE}.tests.workflows.test_workflow_xmipp_ctf_consensus
   scipion3 tests {__MODULE}.tests.workflows.test_workflow_xmipp_ctf_consensus.TestCtfConsensus
 scipion3 tests {__MODULE}.tests.workflows.test_workflow_xmipp_assignment_tiltpairs
   scipion3 tests {__MODULE}.tests.workflows.test_workflow_xmipp_assignment_tiltpairs.TestXmippAssignmentTiltPairsWorkflow
 scipion3 tests {__MODULE}.tests.workflows.test_workflow_xmipp
   scipion3 tests {__MODULE}.tests.workflows.test_workflow_xmipp.TestXmippWorkflow
 scipion3 tests {__MODULE}.tests.test_convert_atom_struct
   scipion3 tests {__MODULE}.tests.test_convert_atom_struct.TestAtomicStructHandler
"""
__DATASETS = ["dataset_1", "dataset_2"]
__ALL_TESTS = [f"test_{i}" for i in range(10)]
__TESTS = __ALL_TESTS[:5]
__TEST_BATCHES = [__ALL_TESTS[5:7], __ALL_TESTS[7:]]

def test_exists_with_error_when_test_search_fails(__mock_run_shell_command, __mock_print):
  error_text = "Test fail"
  __mock_run_shell_command.return_value = (1, error_text)
  with pytest.raises(SystemExit):
    scipion_handler.get_all_tests(__SCIPION, __MODULE)
  __mock_print.assert_called_once_with(
    logger.red(f"{error_text}\nERROR: Test search command failed. Check line above for more detailed info."),
    flush=True
  )

def test_exits_with_error_when_plugin_is_not_installed(__mock_run_shell_command, __mock_print, __mock_exists_module):
  __mock_exists_module.return_value = False
  with pytest.raises(SystemExit):
    scipion_handler.get_all_tests(__SCIPION, __MODULE)
  __mock_print.assert_called_once_with(
    logger.red(f"ERROR: No tests were found for module {__MODULE}. Are you sure this module is properly installed?"),
    flush=True
  )

def test_returns_expected_test_list(__mock_run_shell_command, __mock_exists_module):
  __mock_run_shell_command.return_value = (0, __TEST_LIST_STRING)
  __mock_exists_module.return_value = True
  assert (
    scipion_handler.get_all_tests(__SCIPION, __MODULE) == [
      "workflows.test_workflow_xmipp_rct.TestXmippRCTWorkflow",
      "workflows.test_workflow_xmipp_ctf_consensus.TestCtfConsensus",
      "workflows.test_workflow_xmipp_assignment_tiltpairs.TestXmippAssignmentTiltPairsWorkflow",
      "workflows.test_workflow_xmipp.TestXmippWorkflow",
      "test_convert_atom_struct.TestAtomicStructHandler"
    ]
  ), "Received different tests than expected"

def test_prints_starting_message_when_downloading_datasets(__mock_print, __mock_run_function_in_parallel):
  __mock_run_function_in_parallel.return_value = []
  scipion_handler.download_datasets(__SCIPION, __DATASETS)
  __mock_print.assert_called_once_with(
    logger.blue(f"Downloading {len(__DATASETS)} datasets..."),
    flush=True
  )

def test_exits_with_error_when_downloading_datasets(__mock_print, __mock_run_function_in_parallel):
  __mock_run_function_in_parallel.return_value = [True]
  with pytest.raises(SystemExit):
    scipion_handler.download_datasets(__SCIPION, __DATASETS)
  __mock_print.assert_called_with(
    logger.red("The download of at least one dataset ended with errors. Exiting."),
    flush=True
  )

def test_shows_expected_individual_download_warning_when_downloading_dataset(
  __mock_print,
  __mock_log_warning,
  __mock_run_shell_command
):
  __mock_run_shell_command.return_value = (0, "")
  scipion_handler.__download_dataset(__DATASETS[0], __SCIPION)
  __mock_log_warning.assert_called_once_with(f"Downloading dataset {__DATASETS[0]}...")

def test_exits_with_error_when_downloading_individual_dataset(
  __mock_print,
  __mock_log_warning,
  __mock_run_shell_command
):
  failure_message = "Test fail"
  __mock_run_shell_command.return_value = (1, failure_message)
  scipion_handler.__download_dataset(__DATASETS[0], __SCIPION)
  __mock_print.assert_called_once_with(
    logger.red(f"{failure_message}\nDataset {__DATASETS[0]} download failed with the above message."),
    flush=True
  )

def test_shows_expected_individual_download_success_message_when_downloading_individual_dataset(
  __mock_print,
  __mock_log_warning,
  __mock_run_shell_command
):
  __mock_run_shell_command.return_value = (0, "")
  scipion_handler.__download_dataset(__DATASETS[0], __SCIPION)
  __mock_print.assert_called_once_with(
    logger.green(f"Dataset {__DATASETS[0]} download OK"),
    flush=True
  )

def test_logs_expected_messages_when_running_tests(__mock_print, __mock_run_test_batch):
  scipion_handler.run_tests(__SCIPION, __TESTS, __TEST_BATCHES, 2, __MODULE)
  calls = [
    call(logger.blue("Initial run of non-dependent tests."), flush=True),
    call(logger.blue("Batch of dependent tests 1/2."), flush=True),
    call(logger.blue("Batch of dependent tests 2/2."), flush=True)
  ]
  __mock_print.assert_has_calls(calls)

def test_does_not_log_run_messages_when_running_tests(__mock_print, __mock_run_test_batch):
  scipion_handler.run_tests(__SCIPION, __TESTS, [], 2, __MODULE)
  __mock_print.assert_not_called()

@pytest.mark.parametrize(
  "failed_tests,expected_failed_total",
  [
    pytest.param([[], [], []], []),
    pytest.param([[__TESTS[0]], [], []], [__TESTS[0]]),
    pytest.param([[], [__TEST_BATCHES[0][0]], []], [__TEST_BATCHES[0][0]]),
    pytest.param([[], [], [__TEST_BATCHES[1][0]]], [__TEST_BATCHES[1][0]]),
    pytest.param([[], [__TEST_BATCHES[0][0]], [__TEST_BATCHES[1][0]]], [__TEST_BATCHES[0][0], __TEST_BATCHES[1][0]]),
    pytest.param([[__TESTS[0]], [__TEST_BATCHES[0][0]], [__TEST_BATCHES[1][0]]], [__TESTS[0], __TEST_BATCHES[0][0], __TEST_BATCHES[1][0]]),
    pytest.param([__TESTS.copy(), __TEST_BATCHES[0], []], __TESTS + __TEST_BATCHES[0]),
    pytest.param([__TESTS.copy(), [], __TEST_BATCHES[1]], __TESTS + __TEST_BATCHES[1]),
    pytest.param([[], __TEST_BATCHES[0], __TEST_BATCHES[1]], __TEST_BATCHES[0] + __TEST_BATCHES[1]),
    pytest.param([__TESTS.copy(), __TEST_BATCHES[0], __TEST_BATCHES[1]], __ALL_TESTS),
  ]
)
def test_returns_expected_failed_tests_when_running_tests(failed_tests, expected_failed_total, __mock_print):
  mock_run_test_batch = Mock()
  mock_run_test_batch.side_effect = failed_tests
  with patch(
		"scipion_testrunner.domain.handlers.scipion_handler.__run_test_batch",
		new=mock_run_test_batch
	):
    assert (
      scipion_handler.run_tests(__SCIPION, __TESTS.copy(), __TEST_BATCHES.copy(), 1, __MODULE) == expected_failed_total
    ), "Received different failed tests than expected"

@pytest.mark.parametrize(
  "batch,max_jobs,test_number_text,batch_text",
  [
    pytest.param(__TESTS, 2, 'tests', " in batches of 2 processes"),
    pytest.param(__TESTS, 20, 'tests', f" in batches of {len(__TESTS)} processes"),
    pytest.param([__TESTS[0]], 20, 'test', ""),
    pytest.param([__TESTS[0]], 1, 'test', ""),
    pytest.param(__TESTS, 1, 'tests', " in batches of 1 process")
  ]
)
def test_logs_expected_message_when_running_test_batch(
  batch,
  max_jobs,
  test_number_text,
  batch_text,
  __mock_print,
  __mock_run_function_in_parallel
):
  scipion_handler.__run_test_batch(batch, max_jobs, __SCIPION, __MODULE)
  __mock_print.assert_called_once_with(
    logger.blue(f"Running a total of {len(batch)} {test_number_text} for {__MODULE}{batch_text}..."),
    flush=True
  )

def test_runs_function_in_parallel(__mock_print, __mock_run_function_in_parallel):
  scipion_handler.__run_test_batch(__TESTS, 5, __SCIPION, __MODULE)
  __mock_run_function_in_parallel.assert_called_once_with(
    scipion_handler.__run_test,
    __SCIPION,
    __MODULE,
    parallelizable_params=__TESTS,
    jobs=5
  )

def test_logs_expected_initial_warning_when_running_test(
  __mock_log_warning,
  __mock_run_shell_command,
  __mock_print
):
  scipion_handler.__run_test(__TESTS[0], __SCIPION, __MODULE)
  __mock_log_warning.assert_called_once_with(f"Running test {__TESTS[0]}...")

@pytest.mark.parametrize(
  "return_code,output,expected_message",
  [
    pytest.param(0, "", logger.green(f"Test {__TESTS[0]} OK")),
    pytest.param(1, "AAA", logger.red(f"AAA\nTest {__TESTS[0]} failed with above message."))
  ]
)
def test_logs_expected_message_when_running_test(
  return_code,
  output,
  expected_message,
  __mock_log_warning,
  __mock_run_shell_command,
  __mock_print
):
  __mock_run_shell_command.return_value = (return_code, output)
  scipion_handler.__run_test(__TESTS[0], __SCIPION, __MODULE)
  __mock_print.assert_called_once_with(expected_message, flush=True)

@pytest.mark.parametrize(
  "return_code,expected_return",
  [
    pytest.param(0, None),
    pytest.param(1, __TESTS[0])
  ]
)
def test_returns_expected_output_when_running_test(
  return_code,
  expected_return,
  __mock_log_warning,
  __mock_run_shell_command,
  __mock_print
):
  __mock_run_shell_command.return_value = (return_code, "")
  assert (
    scipion_handler.__run_test(__TESTS[0], __SCIPION, __MODULE) == expected_return
  )

@pytest.mark.parametrize("plugin", [pytest.param(''), pytest.param("test_name")])
def test_returns_expected_test_prefix(plugin):
  assert (
    scipion_handler.__get_test_prefix(plugin) == f'tests {plugin}.tests.'
  )

@pytest.fixture
def __mock_run_shell_command():
  with patch("scipion_testrunner.domain.handlers.shell_handler.run_shell_command") as mock_method:
    mock_method.return_value = (0, "")
    yield mock_method

@pytest.fixture
def __mock_print():
  with patch("builtins.print") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_exists_module():
  with patch("scipion_testrunner.domain.handlers.python_handler.exists_python_module") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_run_function_in_parallel():
  with patch("scipion_testrunner.domain.handlers.python_handler.run_function_in_parallel") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_log_warning():
  with patch("scipion_testrunner.application.logger.Logger.log_warning") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_run_test_batch():
  with patch("scipion_testrunner.domain.handlers.scipion_handler.__run_test_batch") as mock_method:
    mock_method.return_value = []
    yield mock_method
