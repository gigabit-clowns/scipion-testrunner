import os
from subprocess import Popen, PIPE
from typing import Tuple

def run_shell_command(cmd: str) -> Tuple[int, str]:
	"""
	### Runs the given command in a shell.

	#### Params:
	- cmd (str): Command to run.

	#### Returns:
	- (int): Return code.
	- (str): Output of the command, regardless of if it is an error or regular output.
	"""
	process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, env=os.environ)
	process.wait()
	
	ret_code = process.returncode
	output, err = process.communicate()
	output_str = output.decode() if not ret_code and output else err.decode()
	output_str = output_str[:-1] if output_str.endswith('\n') else output_str

	return ret_code, output_str
