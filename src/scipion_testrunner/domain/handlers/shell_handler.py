"""### Functions that interact with the shell."""

from __future__ import annotations

import os
import subprocess


def run_shell_command(cmd: str) -> tuple[int, str]:
    """
    ### Runs the given command in a shell.

    #### Params:
    - cmd (str): Command to run.

    #### Returns:
    - (int): Return code.
    - (str): Output of the command, regardless of if it is an error or regular output.
    """
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=os.environ
    )
    process.wait()

    ret_code = process.returncode
    output, err = process.communicate()
    output_str = output.decode() if not ret_code and output else err.decode()
    output_str = output_str[:-1] if output_str.endswith("\n") else output_str

    return ret_code, output_str
