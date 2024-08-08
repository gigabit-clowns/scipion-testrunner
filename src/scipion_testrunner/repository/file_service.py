import json
from typing import Tuple, List, Dict

from ..application.logger import logger

def read_test_data_file(file_path: str) -> Tuple[List[str], Dict, Dict]:
	"""
	### Returns a list with the necessary datasets for the tests, as well as 
	### an object with the different tests, the situations where to skip them, 
	### and the dependencies between tests.

	#### Params:
	- file_path (str): Path to the test data json file.

	#### Returns:
	- (tuple[list[str], dict, dict]): Tuple containing the list of 
	datasets to download, skippable tests, and dependencies between tests
	"""
	if not file_path:
		logger(logger.yellow("No skippable tests file provided, running all."))
		return [], {}, {}
	try:
		with open(file_path, 'r') as file:
			data_file = json.load(file)
			return data_file.get("datasets", []), data_file.get("skippable", {}), data_file.get("test-dependencies", {})
	except FileNotFoundError:
		logger.log_error(f"ERROR: File '{file_path}' does not exist.")
	except IsADirectoryError:
		logger.log_error(f"ERROR: Path '{file_path}' provided is a directory.")
	except PermissionError:
		logger.log_error(f"ERROR: Permission denied to open file '{file_path}'.")
	except json.JSONDecodeError as e:
		logger.log_error(f"ERROR: Invalid JSON format in file '{file_path}':\n{e}")
	except Exception as e:
		logger.log_error(f"An unexpected error occurred:\n{e}")
