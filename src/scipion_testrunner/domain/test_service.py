from typing import Dict, List

from ..application.logger import logger
from ..repository import scipion_service, file_service, python_service

def run_tests(args: Dict):
    test_list = scipion_service.get_all_tests(args['scipion'], args['plugin'])
    data_sets, skippable_tests = file_service.read_test_data_file(args['testData'])
    logger(f"FULL TESTS: {test_list}")
    skippable_tests = {'dependencies': [
        {'name': 'scipion-chem', 'module': 'pwchem', 'tests': test_list[:5]}
    ]} # TEST
    test_list = __remove_skippable_tests(test_list, skippable_tests, args['noGpu'])
    logger(f"FULL REMAINING TESTS: {test_list}")
    logger(f"DATA SETS: {data_sets}")
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
    test_list = __remove_dependency_tests(test_list, skippable_tests.get('dependencies', []))
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
    if not no_gpu:
        return test_list
    for gpu_test in gpu_test_list:
        if gpu_test in test_list:
            __log_skip_gpu_test(gpu_test)
            test_list.remove(gpu_test)
    return test_list

def __remove_dependency_tests(test_list: List[str], dependency_test_list: List[Dict]) -> List[str]:
    """
    ### Removes all dependency-based tests from the test list if the dependency is not met

    #### Params:
    - test_list (list[str]): Full list of tests
    - dependency_test_list (list[dict]): List of dependency-based tests

    #### Returns:
    - (list[str]): List of tests where dependency-based ones are removed if applicable
    """
    for dependency in dependency_test_list:
        plugin_name = dependency.get('name')
        module_name = dependency.get('module')
        if module_name and python_service.exists_python_module(module_name):
            continue
        for dependency_test in dependency.get("tests", []):
            if dependency_test in test_list:
                __log_skip_dependency_test(dependency_test, plugin_name)
                test_list.remove(dependency_test)
    return test_list

def __log_skip_gpu_test(test_name: str):
    __log_skip_test(test_name, "Needs GPU")

def __log_skip_dependency_test(test_name: str, dependency: str):
    dependency_name_message = f"with plugin {dependency}" if dependency else ""
    __log_skip_test(test_name, f"Unmet dependency{dependency_name_message}")

def __log_skip_test(test_name: str, custom_text: str):
    logger.log_warning(f"Skipping test {test_name}. Reason: {custom_text}.")
