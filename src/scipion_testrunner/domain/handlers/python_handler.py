import multiprocessing
from typing import Callable, List

from scipion_testrunner.domain.handlers import shell_handler

def exists_python_module(module_name: str) -> bool:
	"""
	### Checks if a given Python module exists

	#### Params:
	- module_name (str): Name of the Python module

	#### Returns:
	- (bool): True if exist, False otherwise
	"""
	return python_command_succeeded(f"import {module_name}")

def python_command_succeeded(command: str) -> bool:
	"""
	### This function executes the given Python command and the status of it.

	#### Params:
	- command (str): Command to test

	#### Returns:
	- (bool): True if command succeeded, False otherwise
	"""
	return not bool(shell_handler.run_shell_command(f"python -c '{command}'")[0])

def run_function_in_parallel(func: Callable, *args, parallelizable_params: List[str], jobs: int=multiprocessing.cpu_count()) -> List:
	"""
	### Runs the given Python function in parallel

	#### Params:
	- func (callable): Function to run in parallel
	- *args (tuple): Contains the params needed by the function
	- parallelizable_params (list[str]): List of main params to parallelize from
	- max_jobs (int): Maximum number of jobs

	#### Returns:
	- (list): Failed commands
	"""
	pool = multiprocessing.Pool(processes=jobs)
	results = [pool.apply_async(func, args=(param,*args)) for param in parallelizable_params]
	failed_commands = []
	for result in results:
		if result.get():
			failed_commands.append(result.get())
	pool.close()
	pool.join()
	return failed_commands
