import os
import subprocess
from unittest.mock import patch, Mock

import pytest

from scipion_testrunner.domain.handlers import shell_handler

__COMMAND = "echo Hi"


def test_calls_popen_when_running_shell_command(__mock_popen):
    shell_handler.run_shell_command(__COMMAND)
    __mock_popen.assert_called_once_with(
        __COMMAND,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        env=os.environ,
    )


def test_calls_popen_wait_when_running_shell_command(__mock_popen):
    shell_handler.run_shell_command(__COMMAND)
    __mock_popen().wait.assert_called_once_with()


def test_calls_popen_communicate_when_running_shell_command(__mock_popen):
    shell_handler.run_shell_command(__COMMAND)
    __mock_popen().communicate.assert_called_once_with()


def test_returns_expected_ok_return_code_when_running_shell_command():
    assert (
        shell_handler.run_shell_command(__COMMAND)[0] == 0
    ), "Command returned a non-zero exit status."


def test_returns_command_output_when_running_shell_command():
    output = shell_handler.run_shell_command(__COMMAND)[1]
    assert (
        __remove_carriage_characters(output) == "Hi"
    ), "Received different output than expected."


def test_returns_expected_error_return_code_when_running_shell_command():
    assert (
        shell_handler.run_shell_command("qwerty")[0] != 0
    ), "Command returned exit status zero."


def __remove_carriage_characters(text: str) -> str:
    """
    ### Returns the given text without carriage characters used in Windows.

    #### Params:
    - text (str): Original text.

    #### Returns:
    - (str): Text without carriage characters.
    """
    return text.replace("\r", "")


@pytest.fixture
def __mock_stdout():
    mock_stdout = Mock()
    mock_stdout.read.return_value = b"Hi\n"
    return mock_stdout


@pytest.fixture
def __mock_stderr():
    mock_stderr = Mock()
    mock_stderr.read.return_value = b"Error\n"
    return mock_stderr


@pytest.fixture
def __mock_popen(__mock_stdout, __mock_stderr):
    with patch("subprocess.Popen") as mock_method:
        mock_process = Mock()
        mock_process.stdout = __mock_stdout()
        mock_process.stderr = __mock_stderr()
        mock_process.wait.return_value = None
        mock_process.communicate.return_value = (0, b"")

        mock_method.return_value = mock_process
        yield mock_method
