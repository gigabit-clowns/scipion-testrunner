from . import shell_service

def exists_python_module(module_name: str) -> bool:
	return python_command_succeeded(f"import {module_name}")

def python_command_succeeded(command: str) -> bool:
	"""
	### This function executes the given Python command and the status of it.

	#### Params:
	- command (str): Command to test

	#### Returns:
	- (bool): True if command succeeded, False otherwise
	"""
	return not bool(shell_service.run_shell_command(f"python -c '{command}'")[0])
