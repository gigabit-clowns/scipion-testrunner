from typing import Dict

from ..logger import logger
from ..scipion import test_getter

def run_tests(args: Dict):
    test_list = test_getter.get_all_tests(args['scipion'], args['plugin'])
    logger(f"FILTERED LINES: {test_list}")
    import sys
    sys.exit(0)
