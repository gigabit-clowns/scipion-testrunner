from typing import List

from ..logger import logger
from ..shell import shell_service, python_service

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
		logger.log_error(output)

	test_list = __get_test_list_from_str(output, plugin_module)
	if not test_list and not python_service.exists_python_module(plugin_module):
		logger.log_error(f"ERROR: No tests were found for module {plugin_module}. Are you sure this module is properly installed?")
	
	return test_list

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
	leading_chars = __get_test_leading_chars(plugin_module)
	for line in lines:
		line = line.lstrip()
		if line.startswith(leading_chars):
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
	return f'scipion3 tests {plugin_module}.tests.'
