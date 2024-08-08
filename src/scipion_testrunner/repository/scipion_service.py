from typing import List, Optional, Dict

from ..application.logger import logger
from . import shell_service, python_service

def get_all_tests(scipion: str, plugin_module: str):
	"""
	### Finds the full list of tests from a given module

	#### Params:
	- scipion (str): Path to Scipion's executable
	- plugin_module (str): Module name of the plugin to obtain tests from

	#### Returns:
	- (list[str]): List of available tests
	"""
	ret_code, output = shell_service.run_shell_command(__get_scipion_test_search_param(scipion, plugin_module))
	if ret_code:
		logger.log_error(f"{output}\nERROR: Test search command failed. Check line above for more detailed info.")

	test_list = __get_test_list_from_str(output, plugin_module)
	if not test_list and not python_service.exists_python_module(plugin_module):
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
	failed_downloads = python_service.run_function_in_parallel(
		__download_dataset,
		scipion,
		parallelizable_params=datasets
	)
	if failed_downloads:
		logger.log_error("The download of at least one dataset ended with errors. Exiting.")

def run_tests(scipion: str, tests: List[str], dependant_tests: Dict):
	"""
	### Runs the given list of tests

	#### Params:
	- scipion (str): Path to Scipion's executable
	- tests (list[str]): List of tests to run
	- dependant_tests (dict): Internal depedencies between tests
	"""

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
	ret_code, output = shell_service.run_shell_command(f"{scipion} testdata --download {dataset}")
	if ret_code:
		logger(logger.red(f"{output}\nDataset {dataset} download failed with the above message."))
		return dataset
	else:
		logger(logger.green(f"Dataset {dataset} download OK"))
