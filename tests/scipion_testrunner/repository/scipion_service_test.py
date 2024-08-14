from typing import Callable, List
from unittest.mock import patch

import pytest

from scipion_testrunner.application.logger import logger
from scipion_testrunner.repository import scipion_service

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
"""
__DATASETS = ["dataset_1", "dataset_2"]

def test_exists_with_error_when_test_search_fails(__mock_run_shell_command, __mock_print):
  error_text = "Test fail"
  __mock_run_shell_command.return_value = (1, error_text)
  with pytest.raises(SystemExit):
    scipion_service.get_all_tests(__SCIPION, __MODULE)
  __mock_print.assert_called_once_with(
    logger.red(f"{error_text}\nERROR: Test search command failed. Check line above for more detailed info."),
    flush=True
  )

def test_exits_with_error_when_plugin_is_not_installed(__mock_run_shell_command, __mock_print, __mock_exists_module):
  __mock_run_shell_command.return_value = (0, "")
  __mock_exists_module.return_value = False
  with pytest.raises(SystemExit):
    scipion_service.get_all_tests(__SCIPION, __MODULE)
  __mock_print.assert_called_once_with(
    logger.red(f"ERROR: No tests were found for module {__MODULE}. Are you sure this module is properly installed?"),
    flush=True
  )

def test_returns_expected_test_list(__mock_run_shell_command, __mock_exists_module):
  __mock_run_shell_command.return_value = (0, __TEST_LIST_STRING)
  __mock_exists_module.return_value = True
  assert (
    scipion_service.get_all_tests(__SCIPION, __MODULE) == [
      "workflows.test_workflow_xmipp_rct.TestXmippRCTWorkflow",
      "workflows.test_workflow_xmipp_ctf_consensus.TestCtfConsensus",
      "workflows.test_workflow_xmipp_assignment_tiltpairs.TestXmippAssignmentTiltPairsWorkflow",
      "workflows.test_workflow_xmipp.TestXmippWorkflow"
    ]
  )

def test_prints_starting_message_when_downloading_datasets(__mock_print, __mock_run_function_in_parallel):
  __mock_run_function_in_parallel.return_value = []
  scipion_service.download_datasets(__SCIPION, __DATASETS)
  __mock_print.assert_called_once_with(
    logger.blue(f"Downloading {len(__DATASETS)} datasets..."),
    flush=True
  )

def test_exits_with_error_when_downloading_datasets(__mock_print, __mock_run_function_in_parallel):
  __mock_run_function_in_parallel.return_value = [True]
  with pytest.raises(SystemExit):
    scipion_service.download_datasets(__SCIPION, __DATASETS)
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
  scipion_service.__download_dataset(__DATASETS[0], __SCIPION)
  __mock_log_warning.assert_called_once_with(f"Downloading dataset {__DATASETS[0]}...")

def test_exits_with_error_when_downloading_individual_dataset(
  __mock_print,
  __mock_log_warning,
  __mock_run_shell_command
):
  failure_message = "Test fail"
  __mock_run_shell_command.return_value = (1, failure_message)
  scipion_service.__download_dataset(__DATASETS[0], __SCIPION)
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
  scipion_service.__download_dataset(__DATASETS[0], __SCIPION)
  __mock_print.assert_called_once_with(
    logger.green(f"Dataset {__DATASETS[0]} download OK"),
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

@pytest.fixture
def __mock_exists_module():
  with patch("scipion_testrunner.repository.python_service.exists_python_module") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_run_function_in_parallel():
  with patch("scipion_testrunner.repository.python_service.run_function_in_parallel") as mock_method:
    yield mock_method

@pytest.fixture
def __mock_log_warning():
  with patch("scipion_testrunner.application.logger.Logger.log_warning") as mock_method:
    yield mock_method
