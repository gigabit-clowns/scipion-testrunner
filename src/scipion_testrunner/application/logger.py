"""
Provides a global logger.
"""

import sys

class Logger:
	"""
	### Logger class for keeping track of messages.
	"""
	__BOLD = "\033[1m"
	__BLUE = "\033[34m"
	__RED = "\033[91m"
	__GREEN = "\033[92m"
	__YELLOW = "\033[93m"
	__END_FORMAT = "\033[0m"
	__FORMATTING_CHARACTERS = [__BOLD, __BLUE, __RED, __GREEN, __YELLOW, __END_FORMAT]

	def __init__(self):
		"""
		### Constructor.
		"""
		self.__log_file = None

	def start_log_file(self, log_path: str):
		"""
		### Initiates the log file.

		#### Params:
		- log_path (str): Path to the log file.
		"""
		self.__log_file = open(log_path, 'w')
 
	def __call__(self, text: str):
		"""
		### Log a message.
		
		#### Params:
		- text (str): Message to be logged. Supports fancy formatting.
		"""
		print(text, flush=True)
		if self.__log_file is not None:
			print(self.__remove_non_printable(text), file=self.__log_file, flush=True)

	def log_warning(self, text: str):
		"""
		### Prints a warning message.

		#### Params:
		- text (str): Warning message to show.
		"""
		self.__call__(self.yellow(self.__remove_non_printable(text)))

	def log_error(self, text: str, ret_code: int=1):
		"""
		### Prints an error message and stops exection.

		#### Params:
		- text (str): Error message to show.
		- ret_code (int): Optional. Return code to end the exection with.
		"""
		self.__call__(self.red(self.__remove_non_printable(text)))
		sys.exit(ret_code)

	def green(self, text: str) -> str:
		"""
		### Returns the given text formatted in green color.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in green color.
		"""
		return self.__format_text(text, self.__GREEN)

	def yellow(self, text: str) -> str:
		"""
		### Returns the given text formatted in yellow color.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in yellow color.
		"""
		return self.__format_text(text, self.__YELLOW)

	def red(self, text: str) -> str:
		"""
		### Returns the given text formatted in red color.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in red color.
		"""
		return self.__format_text(text, self.__RED)

	def blue(self, text: str) -> str:
		"""
		### Returns the given text formatted in blue color.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in blue color.
		"""
		return self.__format_text(text, self.__BLUE)

	def bold(self, text: str) -> str:
		"""
		### Returns the given text formatted in bold.

		#### Params:
		- text (str): Text to format.

		#### Returns:
		- (str): Text formatted in bold.
		"""
		return self.__format_text(text, self.__BOLD)
	
	def __format_text(self, text: str, format_code: str) -> str:
		"""
		### Returns the given text formatted in bold.

		#### Params:
		- text (str): Text to format.
		- format_code (str): Formatting character.

		#### Returns:
		- (str): Text formatted in bold.
		"""
		return f"{format_code}{text}{self.__END_FORMAT}"

	def __remove_non_printable(self, text: str) -> str:
		"""
		### Returns the given text without non printable characters.

		#### Params:
		- text (str): Text to remove format.

		#### Returns:
		- (str): Text without format.
		"""
		for formatting_char in self.__FORMATTING_CHARACTERS:
			text = text.replace(formatting_char, "")
		return text

logger = Logger()
