import argparse
import multiprocessing
import os

from . import runTests

__SCIPION_PARAM_NAME = "scipion"
__PLUGIN_PARAM_NAME = "plugin"
__JOBS_PARAM_NAME = "jobs"
__NO_GPU_PARAM_NAME = "noGpu"
__TEST_DATA_PARAM_NAME = "testData"

def __generate_parser():
	"""
	### Generates an argument parser for the test runner

	#### Returns:
	- (ArgumentParser): Argument parser
	"""
	epilog = "Example 1: python -m scipion-testrunner /path/to/scipion myModule -j 2"
	epilog += f"\nExample 2: python -m scipion-testrunner /path/to/scipion myModule --{__NO_GPU_PARAM_NAME}"
	return argparse.ArgumentParser(
		epilog=epilog,
		formatter_class=argparse.RawDescriptionHelpFormatter
	)


def __add_params(parser: argparse.ArgumentParser):
	"""
	### Inserts the params into the given parser

	#### Params:
	- parser (ArgumentParser): Argument parser

	#### Returns:
	- (ArgumentParser): Argument parser with inserted params
	"""
	parser.add_argument(__SCIPION_PARAM_NAME, help="Path to Scipion executable, relative or absolute")
	parser.add_argument(__PLUGIN_PARAM_NAME, help="Name of the plugin's Python module")
	parser.add_argument("-j", f"--{__JOBS_PARAM_NAME}", type=int, default=multiprocessing.cpu_count(), help="Number of jobs. Defaults to max available")
	parser.add_argument(f"--{__NO_GPU_PARAM_NAME}", action='store_true', help="If set, no tests that need a GPU will run. Use it in enviroments where a GPU cannot be accessed.")
	parser.add_argument(f"--{__TEST_DATA_PARAM_NAME}", default='', help="Location of the test data JSON file.")
	return parser


def __get_args_from_parser(parser: argparse.ArgumentParser):
	"""
	### Extracts the appropiate values from the given parser

	#### Params:
	- parser (ArgumentParser): Argument parser

	#### Returns:
	- (Namespace): Argument's object
	"""
	args = vars(parser.parse_args())
	if __TEST_DATA_PARAM_NAME in args:
		args[__TEST_DATA_PARAM_NAME] = os.path.abspath(args[__TEST_DATA_PARAM_NAME])
	return args


def main():
	parser = __generate_parser()
	parser = __add_params(parser)
	args = __get_args_from_parser(parser)
	runTests.main(args)
