import multiprocessing
from typing import List, Optional

from scipion_testrunner.application.logger import logger
from scipion_testrunner.domain.handlers import python_handler, shell_handler

def get_all_tests(scipion: str, plugin_module: str):
	"""
	### Finds the full list of tests from a given module

	#### Params:
	- scipion (str): Path to Scipion's executable
	- plugin_module (str): Module name of the plugin to obtain tests from

	#### Returns:
	- (list[str]): List of available tests
	"""
	ret_code, output = shell_handler.run_shell_command(__get_scipion_test_search_param(scipion, plugin_module))
	if ret_code:
		logger.log_error(f"{output}\nERROR: Test search command failed. Check line above for more detailed info.", ret_code=ret_code)

	test_list = __get_test_list_from_str(output, plugin_module)
	if not test_list and not python_handler.exists_python_module(plugin_module):
		logger.log_error(f"ERROR: No tests were found for module {plugin_module}. Are you sure this module is properly installed?")
	
	return test_list

def download_datasets(scipion: str, datasets: List[str]):
	"""
	### Downloads the given list of datasets

	#### Params:
	- scipion (str): Path to Scipion's executable
	- datasets (list[str]): List of datasets to download
	"""
	logger(logger.blue(f"Downloading {len(datasets)} datasets..."))
	failed_downloads = python_handler.run_function_in_parallel(
		__download_dataset,
		scipion,
		parallelizable_params=datasets,
		jobs=multiprocessing.cpu_count() * 2
	)
	if failed_downloads:
		logger.log_error("The download of at least one dataset ended with errors. Exiting.")

def run_tests(scipion: str, tests: List[str], test_batches: List[List[str]], max_jobs: int, plugin_module: str) -> List[str]:
	"""
	### Runs the given tests and returns the name of the failed ones

	#### Params:
	- scipion (str): Path to Scipion's executable
	- tests (list[str]): List of tests to run
	- test_batches (list[list[str]]): Test batches to run in order
	- max_jobs (int): Maximum number of concurrent jobs
	- plugin_module (str): Module name of the plugin to run tests for

	#### Returns:
	- (list[str]): Names of the tests that failed 
	"""
	if test_batches:
		logger(logger.blue("Initial run of non-dependent tests."))
	failed_tests = __run_test_batch(tests, max_jobs, scipion, plugin_module)

	n_batches = len(test_batches)
	for batch_number in range(n_batches):
		logger(logger.blue(f"Batch of dependent tests {batch_number + 1}/{n_batches}."))
		failed_in_batch = __run_test_batch(test_batches[batch_number], max_jobs, scipion, plugin_module)
		failed_tests.extend(failed_in_batch)
	
	return failed_tests

def __get_test_list_from_str(command_text: str, plugin_module: str) -> List[str]:
	"""
	### Return the list of tests given a command text

	#### Param:
	- command_text (str): Command text containing the list of tests inside it
	- plugin_module (str): Module name of the plugin to obtain tests from

	#### Returns:
	- (list[str]): List of tests present in the command text
	"""
	lines = command_text.split('\n')
	tests = []
	leading_chars = __get_full_test_leading_chars(plugin_module)
	for line in lines:
		line = line.lstrip()
		if __is_test_line(line, plugin_module):
			tests.append(line.replace(leading_chars, ''))
	return tests

def __get_scipion_test_search_param(scipion: str, plugin_module: str) -> str:
	"""
	### Returns the Scipion test search param for a given plugin module.

	#### Params:
	- scipion (str): Path to Scipion's executable
	- plugin_module (str): Module name of the plugin to obtain tests from
	"""
	return f"{scipion} test --grep {plugin_module}"

def __get_test_leading_chars(plugin_module: str) -> str:
	"""
	### Returns the leading characters of every test string

	#### Params:
	- plugin_module (str): Module name of the plugin to obtain tests from

	#### Returns:
	- (str): Leading characters of test strings
	"""
	return f'tests {plugin_module}.tests.'

def __get_full_test_leading_chars(plugin_module: str) -> str:
	"""
	### Returns the leading characters of every full test string

	#### Params:
	- plugin_module (str): Module name of the plugin to obtain tests from

	#### Returns:
	- (str): Leading characters of full test strings
	"""
	return f'scipion3 {__get_test_leading_chars(plugin_module)}'

def __is_test_line(line: str, plugin_module: str) -> bool:
	"""
	### Checks if the given line corresponds to a test

	#### Params:
	- line (str): Line to check
	- plugin_module (str): Module name of the plugin to obtain tests from

	#### Returns:
	- (bool): True if the line corresponds to a test, False otherwise
	"""
	if not line.startswith(__get_full_test_leading_chars(plugin_module)):
		return False
	test_class = line.split(".")[-1]
	return test_class.startswith("Test")

def __download_dataset(dataset: str, scipion: str) -> Optional[str]:
	"""
	### Downloads the given dataset

	#### Params:
	- dataset (str): Dataset to download
	- scipion (str): Path to Scipion's executable
	"""
	logger.log_warning(f"Downloading dataset {dataset}...")
	ret_code, output = shell_handler.run_shell_command(f"{scipion} testdata --download {dataset}")
	if ret_code:
		logger(logger.red(f"{output}\nDataset {dataset} download failed with the above message."))
		return dataset
	else:
		logger(logger.green(f"Dataset {dataset} download OK"))

def __run_test_batch(tests: List[str], max_jobs: int, scipion: str, plugin_module: str) -> List[str]:
	"""
	### Runs the given test batch

	#### Params:
	- tests (list[str]): Tests in the batch
	- max_jobs (int): Maximum number of concurrent jobs
	- scipion (str): Path to Scipion's executable
	- plugin_module (str): Module name of the plugin to run tests for

	#### Returns:
	- (list[str]): Tests that failed
	"""
	batch_size = len(tests)
	jobs = batch_size if batch_size < max_jobs else max_jobs
	test_number_text = f"test{'s' if batch_size > 1 else ''}"
	jobs_text = f"process{'es' if jobs > 1 else ''}"
	batch_text = f" in batches of {jobs} {jobs_text}" if batch_size > 1 else ""
	logger(logger.blue(f"Running a total of {batch_size} {test_number_text} for {plugin_module}{batch_text}..."))
	return python_handler.run_function_in_parallel(__run_test, scipion, plugin_module, parallelizable_params=tests, jobs=jobs)

def __run_test(test: str, scipion: str, plugin_module: str) -> Optional[str]:
	"""
	### Runs a given test

	#### Params:
	- test (str): Test name
	- scipion (str): Path to Scipion's executable
	- plugin_module (str): Module name of the plugin to run test for

	#### Return:
	- (None | str): Test name if there were any errors
	"""
	logger.log_warning(f"Running test {test}...")
	ret_code, output = shell_handler.run_shell_command(f"{scipion} {__get_test_prefix(plugin_module)}{test}")
	if ret_code:
		logger(logger.red(f"{output}\nTest {test} failed with above message."))
		return test
	else:
		logger(logger.green(f"Test {test} OK"))

def __get_test_prefix(plugin_module: str):
	"""
	### Returns Scipion's prefix for test names

	#### Params:
	- plugin_module (str): Module name of the plugin

	#### Returns:
	- (str): Test prefix
	"""
	return f'tests {plugin_module}.tests.'
