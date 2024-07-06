import argparse, multiprocessing, os

from src import runTests

if __name__ == "__main__":
	""" Calls main function when executed. """
	epilog = "Example 1: python script.py /path/to/scipion pwchem -j 2"
	epilog += "\nExample 2: python script.py /path/to/scipion pwchem -noGPU"
	parser = argparse.ArgumentParser(
		epilog=epilog,
		formatter_class=argparse.RawDescriptionHelpFormatter
	)
	parser.add_argument("scipion", help="Path to Scipion executable, relative or absolute")
	parser.add_argument("plugin", help="Name of the plugin's Python module")
	parser.add_argument("-j", "--jobs", type=int, default=multiprocessing.cpu_count(), help="Number of jobs. Defaults to max available")
	parser.add_argument("-noGPU", action='store_true', help="If set, no tests that need a GPU will run. Use it in enviroments where a GPU cannot be accessed.")
	parser.add_argument("-testData", default='', help="Location of the test data JSON file.")
	args = parser.parse_args()

	if args.testData:
		args.testData = os.path.expanduser(args.testData)

	runTests.main(args)
