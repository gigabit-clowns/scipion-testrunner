from unittest.mock import patch, Mock

import pytest

from scipion_testrunner.domain import test_service

__SCIPION_KEY = "scipion"
__SCIPION = __SCIPION_KEY
__PLUGIN_KEY = "plugin"
__PLUGIN = "myplugin"
__NO_GPU_KEY = "noGpu"
__TEST_DATA_KEY = "testData"
__ARGS = {
	__SCIPION_KEY: __SCIPION,
	__PLUGIN_KEY: __PLUGIN,
	__NO_GPU_KEY: False,
	__TEST_DATA_KEY: "test.json"
}
__DATASETS = ["dataset_1", "dataset_2"]
__TESTS = [f"test_{i}" for i in range(10)]
__GPU_KEY = "gpu"
__DEPENDENCIES_KEY = "dependencies"
__OTHERS_KEY = "others"
__SKIPPABLE_GPU = ["test_1", "test_2"]
__SKIPPABLE_DEPENDENCIES = [
	{"name": "testplugin", "module": "pluginmodule", "tests": ["test_5"]}
]
__SKIPPABLE_OTHER = [
	{'test': "test_3", "reason": "Test reason"},
	{'test': "test_4"}
]
__SKIPPABLE = {
	__GPU_KEY: __SKIPPABLE_GPU,
	__DEPENDENCIES_KEY: __SKIPPABLE_DEPENDENCIES,
	__OTHERS_KEY: __SKIPPABLE_OTHER
}
__INTERNAL_DEPENDENCIES = {
	"test_1": ["test_6"],
	"test_7": ["test_8"],
	"test_8": ["test_7"],
	"test_9": ["test_10"]
}

def test_exits_success_when_there_are_not_tests(__mock_get_all_tests, __mock_log_warning):
	__mock_get_all_tests.return_value = []
	with pytest.raises(SystemExit) as exit_status:
		test_service.test_scipion_plugin(__ARGS)
	assert exit_status.value.code == 0

def test_logs_warning_when_there_are_not_tests(__mock_get_all_tests, __mock_log_warning):
	__mock_get_all_tests.return_value = []
	with pytest.raises(SystemExit):
		test_service.test_scipion_plugin(__ARGS)
	__mock_log_warning.assert_called_once_with(f"Module {__PLUGIN} has not tests. Nothing to run.")

def test_exits_success_when_all_tests_get_removed(
	__mock_get_all_tests,
	__mock_read_test_data_file,
	__mock_remove_skippable_tests,
	__mock_log_warning
):
	__mock_remove_skippable_tests.return_value = []
	with pytest.raises(SystemExit) as exit_status:
		test_service.test_scipion_plugin(__ARGS)
	assert exit_status.value.code == 0

def test_logs_warning_when_all_tests_get_removed(
	__mock_get_all_tests,
	__mock_read_test_data_file,
	__mock_remove_skippable_tests,
	__mock_log_warning
):
	__mock_remove_skippable_tests.return_value = []
	with pytest.raises(SystemExit):
		test_service.test_scipion_plugin(__ARGS)
	__mock_log_warning.assert_called_once_with("There are no tests left. Nothing to run.")

def test_calls_download_datasets(
	__mock_get_all_tests,
	__mock_read_test_data_file,
	__mock_remove_skippable_tests,
	__mock_download_datasets,
	__mock_run_tests
):
	__mock_remove_skippable_tests.return_value = __TESTS
	test_service.test_scipion_plugin(__ARGS)
	__mock_download_datasets.assert_called_once_with(__SCIPION, __DATASETS)

def test_calls_run_tests(
	__mock_get_all_tests,
	__mock_read_test_data_file,
	__mock_remove_skippable_tests,
	__mock_download_datasets,
	__mock_run_tests
):
	__mock_remove_skippable_tests.return_value = __TESTS
	test_service.test_scipion_plugin(__ARGS)
	__mock_run_tests.assert_called_once_with(__SCIPION, __TESTS, __INTERNAL_DEPENDENCIES)

@pytest.mark.parametrize(
	"called_function,params",
	[
		pytest.param("__mock_remove_gpu_tests", (__TESTS, __SKIPPABLE_GPU, False)),
		pytest.param("__mock_remove_dependency_tests", (__TESTS, __SKIPPABLE_DEPENDENCIES)),
		pytest.param("__mock_remove_other_tests", (__TESTS, __SKIPPABLE_OTHER))
	]
)
def test_calls_expected_test_removal_function_when_removing_skippable_tests(
	called_function,
	params,
	__mock_remove_gpu_tests,
	__mock_remove_dependency_tests,
	__mock_remove_other_tests
):
	test_service.__remove_skippable_tests(__TESTS.copy(), __SKIPPABLE, False)
	locals()[called_function].assert_called_once_with(*params)

@pytest.mark.parametrize(
	"removal_function",
	[
		pytest.param("__mock_remove_gpu_tests"),
		pytest.param("__mock_remove_dependency_tests"),
		pytest.param("__mock_remove_other_tests")
	]
)
def test_returns_expected_remaining_tests_when_removing_skippable_tests(
	removal_function,
	__mock_remove_gpu_tests,
	__mock_remove_dependency_tests,
	__mock_remove_other_tests
):
	locals()[removal_function].return_value = __TESTS[:1]
	locals()[removal_function].side_effect = None
	assert (
		test_service.__remove_skippable_tests(__TESTS.copy(), __SKIPPABLE, True) == __TESTS[:1]
	), "Received different remaining tests than expected."

def test_logs_skipping_gpu_test(__mock_log_skip_gpu_test):
	test_service.__remove_gpu_tests(__TESTS.copy(), __TESTS[:1], True)
	__mock_log_skip_gpu_test.assert_called_once_with(__TESTS[0])

@pytest.mark.parametrize(
	"to_remove,no_gpu",
	[
		pytest.param(__TESTS[:1], True),
		pytest.param(__TESTS.copy(), True),
		pytest.param(["does_not_exist"], True),
		pytest.param(__TESTS[:1], False)
	]
)
def test_removes_expected_gpu_tests(to_remove, no_gpu, __mock_log_skip_gpu_test):
	remaining = list(set(__TESTS.copy()) - set(to_remove)) if no_gpu else __TESTS
	assert (
		test_service.__remove_gpu_tests(__TESTS.copy(), to_remove, no_gpu).sort() == remaining.sort()
	), "Different remaining tests than expected."

@pytest.mark.parametrize(
	"name,is_plugin",
	[
		pytest.param("test_name", True),
		pytest.param("test_name_2", False),
	]
)
def test_logs_skipping_dependency_test_with_expected_args(name, is_plugin, __mock_exists_python_module, __mock_log_skip_dependency_test):
	test_to_remove = "test_1"
	test_service.__remove_dependency_tests(__TESTS.copy(), [
		{'name': name, 'module': 'test_module', 'isPlugin': is_plugin, 'tests': [test_to_remove]}
	])
	__mock_log_skip_dependency_test.assert_called_once_with(test_to_remove, name, is_plugin=is_plugin)

@pytest.mark.parametrize(
	"exist,to_remove,remaining_tests",
	[
		pytest.param([True, False], __TESTS[:2], [__TESTS[0], *__TESTS[2:]]),
		pytest.param([True, True], __TESTS[:2], __TESTS),
		pytest.param([False, False], __TESTS[:2], __TESTS[2:]),
		pytest.param([True], ["non_existent"], __TESTS),
		pytest.param([False], ["non_existent"], __TESTS)
	]
)
def test_removes_expected_dependency_tests(
	exist,
	to_remove,
	remaining_tests,
	__mock_log_skip_dependency_test
):
	mock_exists_python_module = Mock()
	mock_exists_python_module.side_effect = exist
	dependency_tests = [{
		'name': 'test_name',
		'module': 'test_module',
		'isPlugin': True,
		'tests': [test]
	} for test in to_remove]
	with patch(
		"scipion_testrunner.repository.python_service.exists_python_module",
		new=mock_exists_python_module
	):
		assert (
			test_service.__remove_dependency_tests(__TESTS.copy(), dependency_tests) == remaining_tests
		), "Received different remaining tests than expected."

def test_logs_skipping_other_test(__mock_log_skip_test):
	reason = "test_reason"
	test_service.__remove_other_tests(
		__TESTS.copy(), 
		[{'name': __TESTS[0], "reason": reason}]
	)
	__mock_log_skip_test.assert_called_once_with(__TESTS[0], reason)

@pytest.mark.parametrize(
	"to_remove",
	[
		pytest.param(__TESTS[:1]),
		pytest.param(__TESTS.copy()),
		pytest.param(["does_not_exist"]),
	]
)
def test_removes_expected_other_tests(to_remove, __mock_log_skip_test):
	remaining = list(set(__TESTS.copy()) - set(to_remove))
	other_tests = [{"name": test_name, "reason": "test_reason"} for test_name in to_remove]
	assert (
		test_service.__remove_other_tests(__TESTS.copy(), other_tests).sort() == remaining.sort()
	), "Different remaining tests than expected."

def test_logs_expected_message_when_skipping_gpu_test(__mock_log_skip_test):
	test_service.__log_skip_gpu_test(__TESTS[0])
	__mock_log_skip_test.assert_called_once_with(__TESTS[0], "Needs GPU")

@pytest.mark.parametrize(
	"is_plugin,dependency_name,message",
	[
		pytest.param(True, "test_name", " with plugin test_name"),
		pytest.param(True, "", ""),
		pytest.param(False, "test_name", " with package test_name"),
		pytest.param(False, "", "")
	]
)
def test_logs_expected_message_when_skipping_dependency_test(
	is_plugin,
	dependency_name,
	message,
	__mock_log_skip_test
):
	test_service.__log_skip_dependency_test(__TESTS[0], dependency_name, is_plugin=is_plugin)
	__mock_log_skip_test.assert_called_once_with(__TESTS[0], f"Unmet dependency{message}")

def test_logs_expected_warning_message_when_skipping_test(__mock_log_warning):
	reason = "test_reason"
	test_service.__log_skip_test(__TESTS[0], reason)
	__mock_log_warning.assert_called_once_with(
		f"Skipping test {__TESTS[0]}. Reason: {reason}."
	)

@pytest.fixture
def __mock_get_all_tests():
	with patch("scipion_testrunner.repository.scipion_service.get_all_tests") as mock_method:
		mock_method.return_value = __TESTS
		yield mock_method

@pytest.fixture
def __mock_log_warning():
	with patch("scipion_testrunner.application.logger.Logger.log_warning") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_read_test_data_file():
	with patch("scipion_testrunner.repository.file_service.read_test_data_file") as mock_method:
		mock_method.return_value = (__DATASETS, __SKIPPABLE, __INTERNAL_DEPENDENCIES)
		yield mock_method

@pytest.fixture
def __mock_remove_skippable_tests():
	with patch("scipion_testrunner.domain.test_service.__remove_skippable_tests") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_download_datasets():
	with patch("scipion_testrunner.repository.scipion_service.download_datasets") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_run_tests():
	with patch("scipion_testrunner.repository.scipion_service.run_tests") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_remove_gpu_tests():
	with patch("scipion_testrunner.domain.test_service.__remove_gpu_tests") as mock_method:
		mock_method.side_effect = lambda tests, skippable_gpu, no_gpu: tests
		yield mock_method

@pytest.fixture
def __mock_remove_dependency_tests():
	with patch("scipion_testrunner.domain.test_service.__remove_dependency_tests") as mock_method:
		mock_method.side_effect = lambda tests, skippable_dependency: tests
		yield mock_method

@pytest.fixture
def __mock_remove_other_tests():
	with patch("scipion_testrunner.domain.test_service.__remove_other_tests") as mock_method:
		mock_method.side_effect = lambda tests, skippable_other: tests
		yield mock_method

@pytest.fixture
def __mock_log_skip_gpu_test():
	with patch("scipion_testrunner.domain.test_service.__log_skip_gpu_test") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_exists_python_module(request):
	with patch("scipion_testrunner.repository.python_service.exists_python_module") as mock_method:
		mock_method.return_value = request.param if hasattr(request, "param") else False
		yield mock_method

@pytest.fixture
def __mock_log_skip_dependency_test():
	with patch("scipion_testrunner.domain.test_service.__log_skip_dependency_test") as mock_method:
		yield mock_method

@pytest.fixture
def __mock_log_skip_test():
	with patch("scipion_testrunner.domain.test_service.__log_skip_test") as mock_method:
		yield mock_method
