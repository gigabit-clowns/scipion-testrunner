from unittest.mock import patch

import pytest

from scipion_testrunner.domain import test_service

__SCIPION_KEY = "scipion"
__SCIPION = __SCIPION_KEY
__PLUGIN_KEY = "plugin"
__PLUGIN = "myplugin"
__ARGS = {
	__SCIPION_KEY: __SCIPION,
	__PLUGIN_KEY: __PLUGIN
}
__DATASETS = ["dataset_1", "dataset_2"]
__TESTS = [f"test_{i}" for i in range(10)]
__SKIPPABLE_GPU = ["test_1", "test_2"]
__SKIPPABLE_OTHER = [
	{'test': "test_3", "reason": "Test reason"},
	{'test': "test_4"}
]
__SKIPPABLE_DEPENDENCIES = [
	{"name": "testplugin", "module": "pluginmodule", "tests": ["test_5"]}
]
__INTERNAL_DEPENDENCIES = {
	"test_1": ["test_6"],
	"test_7": ["test_8"],
	"test_8": ["test_7"],
	"test_9": ["test_10"]
}

def test_exits_success_when_there_are_not_tests(__mock_get_all_tests, __mock_print):
	__mock_get_all_tests.return_value = []
	with pytest.raises(SystemExit) as exit_status:
		test_service.test_scipion_plugin(__ARGS)
	assert exit_status.value.code == 0

def test_logs_warning_when_there_are_not_tests(__mock_get_all_tests, __mock_log_warning):
	__mock_get_all_tests.return_value = []
	with pytest.raises(SystemExit) as exit_status:
		test_service.test_scipion_plugin(__ARGS)
	__mock_log_warning.assert_called_once_with(f"Module {__PLUGIN} has not tests. Nothing to run.")

@pytest.fixture
def __mock_get_all_tests():
	with patch("scipion_testrunner.repository.scipion_service.get_all_tests") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_print():
	with patch("builtins.print") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_log_warning():
	with patch("scipion_testrunner.application.logger.Logger.log_warning") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_read_test_data_file():
	with patch("scipion_testrunner.repository.file_service.read_test_data_file") as mock_method:
		mock_method.return_value = (__DATASETS)
		yield mock_method
