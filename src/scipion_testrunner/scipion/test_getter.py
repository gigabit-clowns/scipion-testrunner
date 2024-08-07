import subprocess

def getAllTests(scipion: str, plugin_module: str, test_prefix: str):
	"""
	### Finds the full list of tests from a given module

	#### Params:
	- scipion (str): Path to Scipion's executable
	- plugin_module (str): Module name of the plugin to obtain tests from
	- test_prefix (str): Prefix format for the test names

	#### Returns:
	- (list[str]): List of available tests
	"""
	# Construct the test discovery command
	command = f"{scipion} test --grep {plugin_module}"

	# Run the shell command and capture the output
	try:
		output = subprocess.check_output(command, shell=True, text=True)
	except subprocess.CalledProcessError:
		#printFatalError("ERROR: Test search command failed. Check line above for more detailed info.")
		exit(1)

	# Define test command string variables
	scipionTestsStartingSpaces = '   '

	# Separate lines into a list
	lines = output.split('\n')

	# For each line, keep only the ones about individual tests in a reduced form
	filtered_lines = []
	for line in lines:
		if line.startswith(scipionTestsStartingSpaces):
			filtered_lines.append(line.replace(f'{scipionTestsStartingSpaces}scipion3 {test_prefix}', ''))
	
	# If no tests were found, check if module was not found or if plugin has no tests
	if not filtered_lines:
		pass
		# If import caused an error, module was not found
		#if not testPythonCommand(scipion, f"import {plugin_module}"):
		#	printFatalError(f"ERROR: No tests were found for module {plugin_module}. Are you sure this module is properly installed?")
	
	# Return full list of tests
	return filtered_lines