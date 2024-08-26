import sys
from typing import Dict, List, Tuple

from ..application.logger import logger
from ..repository import scipion_service, file_service, python_service

def test_scipion_plugin(args: Dict):
	tests = scipion_service.get_all_tests(args['scipion'], args['plugin'])
	if not tests:
		logger.log_warning(f"Module {args['plugin']} has not tests. Nothing to run.")
		sys.exit(0)
	data_sets, skippable_tests, tests_with_deps = file_service.read_test_data_file(args['testData'])
	tests = __remove_skippable_tests(tests, skippable_tests, args['noGpu'])
	if not tests:
		logger.log_warning("There are no tests left. Nothing to run.")
		sys.exit(0)
	if data_sets:
		scipion_service.download_datasets(args['scipion'], data_sets)
	tests, tests_with_deps = __remove_unmet_internal_dependency_tests(tests, tests_with_deps)
	scipion_service.run_tests(args['scipion'], tests, tests_with_deps)

def __remove_skippable_tests(tests: List[str], skippable_tests: Dict, no_gpu: bool) -> List[str]:
	"""
	### Removes all the tests that apply from the full test list

	#### Params:
	- tests (list[str]): Full list of tests
	- skippable_tests (dict): Dictionary containing the different types of skippable tests
	- no_gpu (bool): If True, GPU-based tests must be removed

	#### Returns:
	- (list[str]): List of tests where skippable ones are removed if applicable
	"""
	tests = __remove_gpu_tests(tests, skippable_tests.get('gpu', []), no_gpu)
	tests = __remove_dependency_tests(tests, skippable_tests.get('dependencies', []))
	return __remove_other_tests(tests, skippable_tests.get('others', []))

def __remove_gpu_tests(tests: List[str], gpu_tests: List[str], no_gpu: bool) -> List[str]:
	"""
	### Removes the GPU-based tests from the test list if applicable

	#### Params:
	- tests (list[str]): Full list of tests
	- gpu_tests (list[str]): List of GPU-base tests
	- no_gpu (bool): If True, GPU-based tests must be removed

	#### Returns:
	- (list[str]): List of tests where GPU-based ones are removed if applicable
	"""
	if not no_gpu:
		return tests
	for gpu_test in gpu_tests:
		if gpu_test in tests:
			__log_skip_gpu_test(gpu_test)
			tests.remove(gpu_test)
	return tests

def __remove_dependency_tests(tests: List[str], dependency_tests: List[Dict]) -> List[str]:
	"""
	### Removes all dependency-based tests from the test list if the dependency is not met

	#### Params:
	- tests (list[str]): Full list of tests
	- dependency_tests (list[dict]): List of dependency-based tests

	#### Returns:
	- (list[str]): List of tests where dependency-based ones are removed if applicable
	"""
	for dependency in dependency_tests:
		plugin_name = dependency.get('name')
		module_name = dependency.get('module')
		is_plugin = dependency.get('isPlugin', True)
		if module_name and python_service.exists_python_module(module_name):
			continue
		for dependency_test in dependency.get("tests", []):
			if dependency_test in tests:
				__log_skip_dependency_test(dependency_test, plugin_name, is_plugin=is_plugin)
				tests.remove(dependency_test)
	return tests

def __remove_other_tests(tests: List[str], other_tests: List[Dict]) -> List[str]:
	"""
	### Removes other tests from the test list

	#### Params:
	- tests (list[str]): Full list of tests
	- other_tests (list[dict]): List of other tests

	#### Returns:
	- (list[str]): List of tests where other tests have been removed
	"""
	for other_test in other_tests:
		test_name = other_test.get("name")
		reason = other_test.get("reason")
		if test_name and test_name in tests:
			__log_skip_test(test_name, reason)
			tests.remove(test_name)
	return tests

def __log_skip_gpu_test(test_name: str):
	"""
	### Logs the removal of a GPU-based test

	#### Params:
	- test_name (str): Name of the test to skip
	"""
	__log_skip_test(test_name, "Needs GPU")

def __log_skip_dependency_test(test_name: str, dependency: str, is_plugin: bool=True):
	"""
	### Logs the removal of a dependency-based test

	#### Params:
	- test_name (str): Name of the test to skip
	- dependency (str): Name of the plugin or module the test deppends on
	- is_plugin (bool): If True, the package is a plugin. Otherwise, is a regular python package.
	"""
	package_type = 'plugin' if is_plugin else 'package'
	dependency_name_message = f" with {package_type} {dependency}" if dependency else ""
	__log_skip_test(test_name, f"Unmet dependency{dependency_name_message}")

def __log_skip_test(test_name: str, custom_text: str):
	"""
	### Logs the removal of a test

	#### Params:
	- test_name (str): Name of the test to skip
	- custom_text (str): Custom reason why the test is being skipped
	"""
	reason_text = f"Reason: {custom_text}" if custom_text else "No reason provided"
	logger.log_warning(f"Skipping test {test_name}. {reason_text}.")

def __remove_unmet_internal_dependency_tests(tests: List[str], tests_with_deps: Dict[str, List[str]]) -> Tuple[List[str], Dict[str, List[str]]]:
	"""
	### Removes all the tests that have unmet dependencies

	#### Params:
	- tests (list[str]): Full list of tests
	- tests_with_deps (dict[str, list[str]]): Dictionary containing tests with their dependencies

	#### Returns:
	- (list[str]): All remaining tests
	- (dict[str, list[str]]): Remaining tests with their met dependencies
	"""
	has_been_modified = False
	for test, deps in list(tests_with_deps.items()):
		non_met_deps = list(set(deps) - set(tests))
		if non_met_deps:
			has_been_modified = True
			del tests_with_deps[test]
			if test in tests:
				non_met_deps_text = f"'{non_met_deps[0]}'" if len(non_met_deps) == 1 else  ", ".join([
					f"'{test}'" for test in non_met_deps
				])
				__log_skip_test(test, f"Missing dependency with tests: {non_met_deps_text}")
				tests.remove(test)
	if has_been_modified:
		return __remove_unmet_internal_dependency_tests(tests, tests_with_deps)
	return tests, tests_with_deps
