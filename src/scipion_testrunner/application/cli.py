import argparse
import multiprocessing
import os
from typing import Dict

from scipion_testrunner.domain import test_service

def __generate_parser() -> argparse.ArgumentParser:
	"""
	### Generates an argument parser for the test runner

	#### Returns:
	- (ArgumentParser): Argument parser
	"""
	epilog = "Example 1: python -m scipion-testrunner /path/to/scipion myModule -j 2"
	epilog += f"\nExample 2: python -m scipion-testrunner /path/to/scipion myModule --{test_service.NO_GPU_PARAM_NAME}"
	return argparse.ArgumentParser(
		prog="scipion_testrunner",
		epilog=epilog,
		formatter_class=argparse.RawDescriptionHelpFormatter
	)


def __add_params(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
	"""
	### Inserts the params into the given parser

	#### Params:
	- parser (ArgumentParser): Argument parser

	#### Returns:
	- (ArgumentParser): Argument parser with inserted params
	"""
	parser.add_argument(test_service.SCIPION_PARAM_NAME, help="Path to Scipion executable, relative or absolute")
	parser.add_argument(test_service.PLUGIN_PARAM_NAME, help="Name of the plugin's Python module")
	parser.add_argument("-j", f"--{test_service.JOBS_PARAM_NAME}", type=int, default=multiprocessing.cpu_count(), help="Number of jobs. Defaults to max available")
	parser.add_argument(f"--{test_service.NO_GPU_PARAM_NAME}", action='store_true', help="If set, no tests that need a GPU will run. Use it in enviroments where a GPU cannot be accessed.")
	parser.add_argument(f"--{test_service.TEST_DATA_PARAM_NAME}", default='', help="Location of the test data JSON file.")
	return parser


def __get_args_from_parser(parser: argparse.ArgumentParser) -> Dict:
	"""
	### Extracts the appropiate values from the given parser

	#### Params:
	- parser (ArgumentParser): Argument parser

	#### Returns:
	- (Namespace): Argument's object
	"""
	args = vars(parser.parse_args())
	if args[test_service.TEST_DATA_PARAM_NAME]:
		args[test_service.TEST_DATA_PARAM_NAME] = os.path.abspath(args[test_service.TEST_DATA_PARAM_NAME])
	return args


def main():
	parser = __generate_parser()
	parser = __add_params(parser)
	args = __get_args_from_parser(parser)
	test_service.test_scipion_plugin(args)
