import json
from typing import Tuple, List, Dict

from ..application.logger import logger, yellow

def read_test_data_file(file_path: str) -> Tuple[List[str] | None, Dict | None]:
	"""
	### Returns a list with the necessary datasets for the tests, as well as 
	### an object with the different tests and the situations where to skip them.

	#### Params:
	- file_path (str): Path to the test data json file.

	#### Returns:
	- (tuple[list[str] | None, dict | None]): Tuple containing the list of 
	datasets to download and skippable tests 
	"""
	try:
		with open(file_path, 'r') as file:
			data_file = json.load(file)
			return data_file.get("datasets", []), data_file.get("skippable", {})
	except FileNotFoundError:
		logger(yellow("No skippable tests file found, running all."))
		return None, None
	except PermissionError:
		logger.log_error(f"ERROR: Permission denied to open file '{file_path}'.")
	except json.JSONDecodeError as e:
		logger.log_error(f"ERROR: Invalid JSON format in file '{file_path}':\n{e}")
	except Exception as e:
		logger.log_error(f"An unexpected error occurred:\n{e}")
