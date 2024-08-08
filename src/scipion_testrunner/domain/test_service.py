from typing import Dict, List

from ..application.logger import logger
from ..repository import scipion_service, file_service

def run_tests(args: Dict):
    test_list = scipion_service.get_all_tests(args['scipion'], args['plugin'])
    data_sets, skippable_tests = file_service.read_test_data_file(args['testData'])
    skippable_tests = {'noGpu': test_list[:5]} # TEST
    test_list = __remove_skippable_tests(test_list, skippable_tests, args['noGpu'])
    logger(f"DATA SETS: {data_sets}")
    logger(f"SKIPPABLE TESTS: {skippable_tests}")
    import sys
    sys.exit(0)

def __remove_skippable_tests(test_list: List[str], skippable_tests: Dict, no_gpu: bool) -> List[str]:
    """
    ### Removes all the tests that apply from the full test list

    #### Params:
    - test_list (list[str]): Full list of tests
    - skippable_tests (dict): Dictionary containing the different types of skippable tests
    - no_gpu (bool): If True, GPU-based tests must be removed

    #### Returns:
    - (list[str]): List of tests where skippable ones are removed if applicable
    """
    test_list = __remove_gpu_tests(test_list, skippable_tests.get('gpu', []), no_gpu)
    return test_list

def __remove_gpu_tests(test_list: List[str], gpu_test_list: List[str], no_gpu: bool) -> List[str]:
    """
    ### Removes the GPU-based tests from the test list if applicable

    #### Params:
    - test_list (list[str]): Full list of tests
    - gpu_test_list (list[str]): List of GPU-base tests
    - no_gpu (bool): If True, GPU-based tests must be removed

    #### Returns:
    - (list[str]): List of tests where GPU-based ones are removed if applicable
    """
    if no_gpu:
        return list(set(test_list) - set(gpu_test_list))
    return test_list
