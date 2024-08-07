import sys
from typing import Dict

from ..scipion import test_getter

def run_tests(args: Dict):
    filtered_lines = test_getter.get_all_tests(args['scipion'], args['plugin'])
    print(filtered_lines)
    sys.exit(0)
