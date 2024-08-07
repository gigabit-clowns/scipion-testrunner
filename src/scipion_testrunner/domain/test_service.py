from typing import Dict, List

from ..application.logger import logger
from ..repository import scipion_service, file_service

def run_tests(args: Dict):
    test_list = scipion_service.get_all_tests(args['scipion'], args['plugin'])
    data_sets, skippable_tests = file_service.read_test_data_file(args['testData'])
    test_list = __remove_skippable_tests(test_list, skippable_tests)
    logger(f"DATA SETS: {data_sets}")
    logger(f"SKIPPABLE TESTS: {skippable_tests}")
    import sys
    sys.exit(0)

def __remove_skippable_tests(test_list: List[str], skippable_tests: Dict) -> List[str]:
    return test_list
