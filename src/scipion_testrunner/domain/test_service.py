from typing import Dict

from ..logger import logger
from ..repository import scipion_service

def run_tests(args: Dict):
    test_list = scipion_service.get_all_tests(args['scipion'], args['plugin'])
    logger(f"FILTERED LINES: {test_list}")
    import sys
    sys.exit(0)
