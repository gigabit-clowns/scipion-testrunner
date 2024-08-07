import sys
from typing import Dict

from ..scipion import test_getter

def run_tests(args: Dict):
    filtered_lines = test_getter.getAllTests(args['scipion'], args['plugin'], f"tests {args['plugin']}.tests.")
    print(filtered_lines)
    sys.exit(0)
