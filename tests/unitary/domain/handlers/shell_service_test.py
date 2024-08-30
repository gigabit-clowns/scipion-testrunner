from scipion_testrunner.domain.handlers import shell_handler

__COMMAND = 'echo Hi'

def test_returns_expected_ok_return_code():
  assert (
    shell_handler.run_shell_command(__COMMAND)[0] == 0
  ), "Command returned a non-zero exit status."

def test_returns_command_output():
  output = shell_handler.run_shell_command(__COMMAND)[1]
  assert (
    __remove_carriage_characters(output) == "Hi"
  ), "Received different output than expected."

def test_returns_expected_error_return_code():
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
