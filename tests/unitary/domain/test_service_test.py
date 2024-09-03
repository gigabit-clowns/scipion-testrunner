from unittest.mock import patch, Mock, call

import pytest

from scipion_testrunner.application.logger import logger
from scipion_testrunner.configuration import test_data_keys
from scipion_testrunner.domain import test_service

__SCIPION = test_service.SCIPION_PARAM_NAME
__PLUGIN = "myplugin"
__ARGS = {
    test_service.SCIPION_PARAM_NAME: __SCIPION,
    test_service.PLUGIN_PARAM_NAME: __PLUGIN,
    test_service.JOBS_PARAM_NAME: 5,
    test_service.NO_GPU_PARAM_NAME: False,
    test_service.TEST_DATA_PARAM_NAME: "test.json",
}
__DATASETS = ["dataset_1", "dataset_2"]
__TESTS = [f"test_{i}" for i in range(10)]
__SKIPPABLE_GPU = __TESTS[:1]
__SKIPPABLE_DEPENDENCIES = [
    {
        test_data_keys.SKIPPABLE_DEPENDENCIES_NAME_KEY: "testplugin",
        test_data_keys.SKIPPABLE_DEPENDENCIES_MODULE_KEY: "pluginmodule",
        test_data_keys.SKIPPABLE_DEPENDENCIES_TESTS_KEY: ["test_5"],
    }
]
__SKIPPABLE_OTHER = [
    {
        test_data_keys.SKIPPABLE_OTHERS_TEST_KEY: "test_3",
        test_data_keys.SKIPPABLE_OTHERS_REASON_KEY: "Test reason",
    },
    {test_data_keys.SKIPPABLE_OTHERS_TEST_KEY: "test_4"},
]
__SKIPPABLE = {
    test_data_keys.SKIPPABLE_GPU_KEY: __SKIPPABLE_GPU,
    test_data_keys.SKIPPABLE_DEPENDENCIES_KEY: __SKIPPABLE_DEPENDENCIES,
    test_data_keys.SKIPPABLE_OTHERS_KEY: __SKIPPABLE_OTHER,
}
__INTERNAL_DEPENDENCIES = {
    "test_1": ["test_6"],
    "test_7": ["test_8"],
    "test_8": ["test_7"],
    "test_9": ["test_10"],
}


def test_exits_success_when_there_are_not_tests_while_testing_scipion_plugin(
    __mock_get_all_tests, __mock_log_warning
):
    __mock_get_all_tests.return_value = []
    with pytest.raises(SystemExit) as exit_status:
        test_service.test_scipion_plugin(__ARGS)
    assert exit_status.value.code == 0


def test_logs_warning_when_there_are_not_tests_while_testing_scipion_plugin(
    __mock_get_all_tests, __mock_log_warning
):
    __mock_get_all_tests.return_value = []
    with pytest.raises(SystemExit):
        test_service.test_scipion_plugin(__ARGS)
    __mock_log_warning.assert_called_once_with(
        f"Module {__PLUGIN} has not tests. Nothing to run."
    )


def test_exits_success_when_all_tests_get_removed_when_testing_scipion_plugin(
    __mock_get_all_tests,
    __mock_get_test_config,
    __mock_remove_skippable_tests,
    __mock_log_warning,
):
    __mock_remove_skippable_tests.return_value = []
    with pytest.raises(SystemExit) as exit_status:
        test_service.test_scipion_plugin(__ARGS)
    assert exit_status.value.code == 0


def test_logs_warning_when_all_tests_get_removed_when_testing_scipion_plugin(
    __mock_get_all_tests,
    __mock_get_test_config,
    __mock_remove_skippable_tests,
    __mock_log_warning,
):
    __mock_remove_skippable_tests.return_value = []
    with pytest.raises(SystemExit):
        test_service.test_scipion_plugin(__ARGS)
    __mock_log_warning.assert_called_once_with(
        "There are no tests left. Nothing to run."
    )


def test_calls_download_datasets_when_testing_scipion_plugin(
    __mock_get_all_tests,
    __mock_get_test_config,
    __mock_remove_skippable_tests,
    __mock_remove_circular_dependencies,
    __mock_remove_unmet_internal_dependency_tests,
    __mock_download_datasets,
    __mock_run_tests,
    __mock_get_sorted_results,
    __mock_log_result_summary,
    __mock_print,
):
    __mock_remove_skippable_tests.return_value = __TESTS
    test_service.test_scipion_plugin(__ARGS)
    __mock_download_datasets.assert_called_once_with(__SCIPION, __DATASETS)


def test_not_calls_download_datasets_when_testing_scipion_plugin(
    __mock_get_all_tests,
    __mock_get_test_config,
    __mock_remove_skippable_tests,
    __mock_download_datasets,
    __mock_run_tests,
    __mock_get_sorted_results,
    __mock_log_result_summary,
    __mock_print,
):
    __mock_get_test_config.return_value = ([], __SKIPPABLE, __INTERNAL_DEPENDENCIES)
    __mock_remove_skippable_tests.return_value = __TESTS
    test_service.test_scipion_plugin(__ARGS)
    __mock_download_datasets.assert_not_called()


def test_calls_run_tests_when_testing_scipion_plugin(
    __mock_get_all_tests,
    __mock_get_test_config,
    __mock_remove_skippable_tests,
    __mock_remove_circular_dependencies,
    __mock_remove_unmet_internal_dependency_tests,
    __mock_download_datasets,
    __mock_generate_sorted_test_batches,
    __mock_run_tests,
    __mock_log_warning,
    __mock_get_sorted_results,
    __mock_log_result_summary,
    __mock_print,
):
    __mock_remove_skippable_tests.return_value = __TESTS.copy()
    test_service.test_scipion_plugin(__ARGS)
    __mock_run_tests.assert_called_once_with(
        __SCIPION,
        __TESTS,
        [],
        __ARGS[test_service.JOBS_PARAM_NAME],
        __ARGS[test_service.PLUGIN_PARAM_NAME],
    )


def test_calls_log_result_summary_when_testing_scipion_plugin(
    __mock_get_all_tests,
    __mock_get_test_config,
    __mock_remove_skippable_tests,
    __mock_remove_circular_dependencies,
    __mock_remove_unmet_internal_dependency_tests,
    __mock_download_datasets,
    __mock_generate_sorted_test_batches,
    __mock_run_tests,
    __mock_log_warning,
    __mock_get_sorted_results,
    __mock_log_result_summary,
    __mock_print,
):
    __mock_remove_skippable_tests.return_value = __TESTS.copy()
    test_service.test_scipion_plugin(__ARGS)
    __mock_log_result_summary.assert_called_once_with(
        __mock_get_sorted_results.return_value
    )


def test_logs_error_with_failed_tests_when_testing_scipion_plugin(
    __mock_get_all_tests,
    __mock_get_test_config,
    __mock_remove_skippable_tests,
    __mock_remove_circular_dependencies,
    __mock_remove_unmet_internal_dependency_tests,
    __mock_download_datasets,
    __mock_generate_sorted_test_batches,
    __mock_run_tests,
    __mock_log_warning,
    __mock_get_sorted_results,
    __mock_log_result_summary,
    __mock_log_error,
    __mock_print,
):
    __mock_remove_skippable_tests.return_value = __TESTS.copy()
    __mock_run_tests.return_value = __TESTS.copy()
    test_service.test_scipion_plugin(__ARGS)
    __mock_log_error.assert_called_once_with("Some tests ended with errors. Exiting.")


def test_logs_success_message_without_failed_tests_when_testing_scipion_plugin(
    __mock_get_all_tests,
    __mock_get_test_config,
    __mock_remove_skippable_tests,
    __mock_remove_circular_dependencies,
    __mock_remove_unmet_internal_dependency_tests,
    __mock_download_datasets,
    __mock_generate_sorted_test_batches,
    __mock_run_tests,
    __mock_log_warning,
    __mock_get_sorted_results,
    __mock_log_result_summary,
    __mock_print,
):
    __mock_remove_skippable_tests.return_value = __TESTS.copy()
    test_service.test_scipion_plugin(__ARGS)
    __mock_print.assert_called_with(logger.green("\nAll test passed!"), flush=True)


@pytest.mark.parametrize(
    "called_function,params",
    [
        pytest.param("__mock_remove_gpu_tests", (__TESTS, __SKIPPABLE_GPU, False)),
        pytest.param(
            "__mock_remove_dependency_tests", (__TESTS, __SKIPPABLE_DEPENDENCIES)
        ),
        pytest.param("__mock_remove_other_tests", (__TESTS, __SKIPPABLE_OTHER)),
    ],
)
def test_calls_expected_test_removal_function_when_removing_skippable_tests(
    called_function,
    params,
    __mock_remove_gpu_tests,
    __mock_remove_dependency_tests,
    __mock_remove_other_tests,
):
    test_service.__remove_skippable_tests(__TESTS.copy(), __SKIPPABLE, False)
    locals()[called_function].assert_called_once_with(*params)


@pytest.mark.parametrize(
    "removal_function",
    [
        pytest.param("__mock_remove_gpu_tests"),
        pytest.param("__mock_remove_dependency_tests"),
        pytest.param("__mock_remove_other_tests"),
    ],
)
def test_returns_expected_remaining_tests_when_removing_skippable_tests(
    removal_function,
    __mock_remove_gpu_tests,
    __mock_remove_dependency_tests,
    __mock_remove_other_tests,
):
    locals()[removal_function].return_value = __TESTS[:1]
    locals()[removal_function].side_effect = None
    assert (
        test_service.__remove_skippable_tests(__TESTS.copy(), __SKIPPABLE, True)
        == __TESTS[:1]
    ), "Received different remaining tests than expected."


def test_logs_skipping_gpu_test(__mock_log_skip_gpu_test):
    test_service.__remove_gpu_tests(__TESTS.copy(), __TESTS[:1], True)
    __mock_log_skip_gpu_test.assert_called_once_with(__TESTS[0])


@pytest.mark.parametrize(
    "to_remove,no_gpu",
    [
        pytest.param(__TESTS[:1], True),
        pytest.param(__TESTS.copy(), True),
        pytest.param(["does_not_exist"], True),
        pytest.param(__TESTS[:1], False),
    ],
)
def test_removes_expected_gpu_tests(to_remove, no_gpu, __mock_log_skip_gpu_test):
    remaining = list(set(__TESTS.copy()) - set(to_remove)) if no_gpu else __TESTS
    assert (
        test_service.__remove_gpu_tests(__TESTS.copy(), to_remove, no_gpu).sort()
        == remaining.sort()
    ), "Different remaining tests than expected."


@pytest.mark.parametrize(
    "name,is_plugin",
    [
        pytest.param("test_name", True),
        pytest.param("test_name_2", False),
    ],
)
def test_logs_skipping_dependency_test_with_expected_args(
    name, is_plugin, __mock_exists_python_module, __mock_log_skip_dependency_test
):
    test_to_remove = "test_1"
    test_service.__remove_dependency_tests(
        __TESTS.copy(),
        [
            {
                test_data_keys.SKIPPABLE_DEPENDENCIES_NAME_KEY: name,
                test_data_keys.SKIPPABLE_DEPENDENCIES_MODULE_KEY: "test_module",
                test_data_keys.SKIPPABLE_DEPENDENCIES_IS_PLUGIN_KEY: is_plugin,
                test_data_keys.SKIPPABLE_DEPENDENCIES_TESTS_KEY: [test_to_remove],
            }
        ],
    )
    __mock_log_skip_dependency_test.assert_called_once_with(
        test_to_remove, name, is_plugin=is_plugin
    )


@pytest.mark.parametrize(
    "exist,to_remove,remaining_tests",
    [
        pytest.param([True, False], __TESTS[:2], [__TESTS[0], *__TESTS[2:]]),
        pytest.param([True, True], __TESTS[:2], __TESTS),
        pytest.param([False, False], __TESTS[:2], __TESTS[2:]),
        pytest.param([True], ["non_existent"], __TESTS),
        pytest.param([False], ["non_existent"], __TESTS),
    ],
)
def test_removes_expected_dependency_tests(
    exist, to_remove, remaining_tests, __mock_log_skip_dependency_test
):
    mock_exists_python_module = Mock()
    mock_exists_python_module.side_effect = exist
    dependency_tests = [
        {
            test_data_keys.SKIPPABLE_DEPENDENCIES_NAME_KEY: "test_name",
            test_data_keys.SKIPPABLE_DEPENDENCIES_MODULE_KEY: "test_module",
            test_data_keys.SKIPPABLE_DEPENDENCIES_IS_PLUGIN_KEY: True,
            test_data_keys.SKIPPABLE_DEPENDENCIES_TESTS_KEY: [test],
        }
        for test in to_remove
    ]
    with patch(
        "scipion_testrunner.domain.handlers.python_handler.exists_python_module",
        new=mock_exists_python_module,
    ):
        assert (
            test_service.__remove_dependency_tests(__TESTS.copy(), dependency_tests)
            == remaining_tests
        ), "Received different remaining tests than expected."


def test_logs_skipping_other_test(__mock_log_skip_test):
    reason = "test_reason"
    test_service.__remove_other_tests(
        __TESTS.copy(),
        [
            {
                test_data_keys.SKIPPABLE_OTHERS_TEST_KEY: __TESTS[0],
                test_data_keys.SKIPPABLE_OTHERS_REASON_KEY: reason,
            }
        ],
    )
    __mock_log_skip_test.assert_called_once_with(__TESTS[0], reason)


@pytest.mark.parametrize(
    "to_remove",
    [
        pytest.param(__TESTS[:1]),
        pytest.param(__TESTS.copy()),
        pytest.param(["does_not_exist"]),
    ],
)
def test_removes_expected_other_tests(to_remove, __mock_log_skip_test):
    remaining = list(set(__TESTS.copy()) - set(to_remove))
    other_tests = [
        {
            test_data_keys.SKIPPABLE_OTHERS_TEST_KEY: test_name,
            test_data_keys.SKIPPABLE_OTHERS_REASON_KEY: "test_reason",
        }
        for test_name in to_remove
    ]
    assert (
        test_service.__remove_other_tests(__TESTS.copy(), other_tests).sort()
        == remaining.sort()
    ), "Different remaining tests than expected."


def test_logs_expected_message_when_skipping_gpu_test(__mock_log_skip_test):
    test_service.__log_skip_gpu_test(__TESTS[0])
    __mock_log_skip_test.assert_called_once_with(__TESTS[0], "Needs GPU")


@pytest.mark.parametrize(
    "is_plugin,dependency_name,message",
    [
        pytest.param(True, "test_name", " with plugin test_name"),
        pytest.param(True, "", ""),
        pytest.param(False, "test_name", " with package test_name"),
        pytest.param(False, "", ""),
    ],
)
def test_logs_expected_message_when_skipping_dependency_test(
    is_plugin, dependency_name, message, __mock_log_skip_test
):
    test_service.__log_skip_dependency_test(
        __TESTS[0], dependency_name, is_plugin=is_plugin
    )
    __mock_log_skip_test.assert_called_once_with(
        __TESTS[0], f"Unmet dependency{message}"
    )


@pytest.mark.parametrize(
    "reason,reason_message",
    [
        pytest.param("test_reason", "Reason: test_reason"),
        pytest.param("", "No reason provided"),
        pytest.param(None, "No reason provided"),
    ],
)
def test_logs_expected_warning_message_when_skipping_test(
    reason, reason_message, __mock_log_warning
):
    test_service.__log_skip_test(__TESTS[0], reason)
    __mock_log_warning.assert_called_once_with(
        f"Skipping test {__TESTS[0]}. {reason_message}."
    )


@pytest.mark.parametrize(
    "tests_with_dependencies,expected_tests",
    [
        pytest.param({}, __TESTS),
        pytest.param({__TESTS[0]: ["non_existent"]}, __TESTS[1:]),
        pytest.param(
            {__TESTS[0]: ["non_existent"], __TESTS[1]: [__TESTS[-1]]}, __TESTS[1:]
        ),
        pytest.param(
            {__TESTS[0]: ["non_existent"], __TESTS[1]: [__TESTS[0]]}, __TESTS[2:]
        ),
        pytest.param(
            {__TESTS[0]: [__TESTS[1]], __TESTS[1]: ["non_existent"]}, __TESTS[2:]
        ),
        pytest.param(
            {
                __TESTS[0]: ["non_existent"],
                __TESTS[1]: [__TESTS[0]],
                __TESTS[2]: [__TESTS[1]],
            },
            __TESTS[3:],
        ),
    ],
)
def test_removes_expected_internal_dependency_tests(
    tests_with_dependencies, expected_tests, __mock_log_skip_test
):
    assert (
        test_service.__remove_unmet_internal_dependency_tests(
            __TESTS.copy(), tests_with_dependencies
        )[0]
        == expected_tests
    ), "Removed different number of tests than expected."


@pytest.mark.parametrize(
    "tests,tests_text",
    [
        pytest.param(["my_random_test"], "'my_random_test'"),
        pytest.param(["random_1", "random_2"], "'random_1', 'random_2'"),
    ],
)
def test_logs_expected_internal_dependency_test_removal(
    tests, tests_text, __mock_log_skip_test
):
    test_service.__remove_unmet_internal_dependency_tests(
        __TESTS.copy(), {__TESTS[0]: tests}
    )
    __mock_log_skip_test.assert_called_once_with(
        __TESTS[0], f"Missing dependency with tests: {tests_text}"
    )


@pytest.mark.parametrize(
    "test_name,dependencies,expected_path",
    [
        pytest.param(__TESTS[0], {}, []),
        pytest.param(__TESTS[0], {__TESTS[0]: ["random_test"]}, []),
        pytest.param(
            __TESTS[0],
            {__TESTS[0]: [__TESTS[-1]], __TESTS[-1]: [__TESTS[0]]},
            [__TESTS[0], __TESTS[-1], __TESTS[0]],
        ),
        pytest.param(
            __TESTS[0], {__TESTS[1]: [__TESTS[-1]], __TESTS[-1]: [__TESTS[1]]}, []
        ),
        pytest.param(
            __TESTS[0],
            {
                __TESTS[0]: [__TESTS[1]],
                __TESTS[1]: [__TESTS[-1]],
                __TESTS[-1]: [__TESTS[1]],
            },
            [__TESTS[1], __TESTS[-1], __TESTS[1]],
        ),
        pytest.param(__TESTS[0], {__TESTS[0]: [__TESTS[0]]}, [__TESTS[0], __TESTS[0]]),
    ],
)
def test_returns_expected_circular_dependencies(test_name, dependencies, expected_path):
    assert (
        test_service.__find_circular_dependency(test_name, dependencies)
        == expected_path
    ), "Received circular dependency path was not expected"


@pytest.mark.parametrize(
    "dependencies,expected_tests",
    [
        pytest.param({}, __TESTS),
        pytest.param({__TESTS[0]: [__TESTS[0]]}, __TESTS[1:]),
        pytest.param({__TESTS[0]: [__TESTS[1]], __TESTS[1]: [__TESTS[0]]}, __TESTS[2:]),
        pytest.param(
            {
                __TESTS[0]: [__TESTS[1]],
                __TESTS[1]: [__TESTS[2]],
                __TESTS[2]: [__TESTS[1]],
            },
            [__TESTS[0]] + __TESTS[3:],
        ),
    ],
)
def test_returns_expected_non_circular_dependency_tests(
    dependencies, expected_tests, __mock_log_skip_test
):
    assert (
        test_service.__remove_circular_dependencies(__TESTS.copy(), dependencies)[0]
        == expected_tests
    ), "Received different tests than expected"


def test_logs_expected_circular_dependency_message(__mock_log_skip_test):
    test_service.__remove_circular_dependency(
        __TESTS.copy(), {__TESTS[0]: [__TESTS[0]]}, [__TESTS[0], __TESTS[0]]
    )
    __mock_log_skip_test.assert_called_once_with(
        __TESTS[0], f"It has a circular dependency: {__TESTS[0]} --> {__TESTS[0]}"
    )


def test_does_not_log_non_existing_tests_in_circular_path(__mock_log_skip_test):
    test_name = "non_existent"
    test_service.__remove_circular_dependency(
        __TESTS.copy(), {test_name: [test_name]}, [test_name, test_name]
    )
    __mock_log_skip_test.assert_not_called()


@pytest.mark.parametrize(
    "test_with_deps,expected_batch",
    [
        pytest.param(
            {__TESTS[0]: [__TESTS[-1]], __TESTS[1]: [__TESTS[0]]}, [__TESTS[0]]
        ),
        pytest.param(
            {__TESTS[0]: [__TESTS[-1]], __TESTS[1]: [__TESTS[2]]},
            [__TESTS[0], __TESTS[1]],
        ),
        pytest.param({__TESTS[0]: [__TESTS[1]], __TESTS[1]: [__TESTS[0]]}, []),
        pytest.param({__TESTS[0]: [__TESTS[0]]}, []),
    ],
)
def test_returns_expected_batch(test_with_deps, expected_batch):
    assert (
        test_service.__get_test_batch(test_with_deps) == expected_batch
    ), "Received different batch than expected"


@pytest.mark.parametrize(
    "test_with_deps,expected_tests,expected_batches",
    [
        pytest.param(
            {__TESTS[0]: [__TESTS[-1]], __TESTS[1]: [__TESTS[0]]},
            __TESTS[2:],
            [[__TESTS[0]], [__TESTS[1]]],
        ),
        pytest.param(
            {__TESTS[0]: [__TESTS[-1]], __TESTS[1]: [__TESTS[2]]},
            __TESTS[2:],
            [[__TESTS[0], __TESTS[1]]],
        ),
        pytest.param({__TESTS[0]: [__TESTS[1]], __TESTS[1]: [__TESTS[0]]}, __TESTS, []),
        pytest.param({__TESTS[0]: [__TESTS[0]]}, __TESTS, []),
        pytest.param({__TESTS[0]: ["non_existing"]}, __TESTS[1:], [[__TESTS[0]]]),
        pytest.param({"non_existing": [__TESTS[0]]}, __TESTS, [["non_existing"]]),
    ],
)
def test_returns_expected_sorted_batches(
    test_with_deps, expected_tests, expected_batches
):
    assert test_service.__generate_sorted_test_batches(
        __TESTS.copy(), test_with_deps
    ) == (
        expected_tests,
        expected_batches,
    ), "Received different sorted batches than expected"


def test_returns_expected_grouped_tests():
    file1_name = "file1"
    file2_name = "file2"
    assert test_service.__group_tests_by_file(
        [
            f"{file1_name}.{__TESTS[0]}",
            f"{file1_name}.{__TESTS[1]}",
            f"{file2_name}.{__TESTS[0]}",
            f"folder.{file1_name}.{__TESTS[0]}",
        ]
    ) == {
        file1_name: [__TESTS[0], __TESTS[1]],
        file2_name: [__TESTS[0]],
        f"folder.{file1_name}": [__TESTS[0]],
    }, "Received different test grouping than expected"


def test_returns_expected_sorted_results():
    file1_name = "file1"
    file2_name = "file2"
    file3_name = "file3"
    assert test_service.__get_sorted_results(
        [
            f"{file1_name}.{__TESTS[0]}",
            f"{file1_name}.{__TESTS[1]}",
            f"{file2_name}.{__TESTS[0]}",
            f"{file3_name}.{__TESTS[0]}",
        ],
        [f"{file1_name}.{__TESTS[1]}", f"{file3_name}.{__TESTS[0]}"],
    ) == {
        file1_name: {"passed": [__TESTS[0]], "failed": [__TESTS[1]]},
        file2_name: {"passed": [__TESTS[0]], "failed": []},
        file3_name: {"passed": [], "failed": [__TESTS[0]]},
    }, "Received different result order than expected"


def test_logs_expected_messages_in_summary_report(__mock_print):
    file1_name = "file1"
    file2_name = "file2"
    file3_name = "file3"
    calls = [
        call("SUMMARY:", flush=True),
        call(f"{file1_name}: [1 / 3]", flush=True),
        call(logger.red(f"\tFailed tests: {__TESTS[1]} {__TESTS[2]}"), flush=True),
        call(f"{file2_name}: [1 / 1]", flush=True),
        call(f"{file3_name}: [0 / 1]", flush=True),
        call(logger.red(f"\tFailed tests: {__TESTS[0]}"), flush=True),
    ]
    test_service.__log_result_summary(
        {
            file1_name: {"passed": [__TESTS[0]], "failed": [__TESTS[1], __TESTS[2]]},
            file2_name: {"passed": [__TESTS[0]], "failed": []},
            file3_name: {"passed": [], "failed": [__TESTS[0]]},
        }
    )
    __mock_print.assert_has_calls(calls)


@pytest.fixture
def __mock_get_all_tests():
    with patch(
        "scipion_testrunner.domain.handlers.scipion_handler.get_all_tests"
    ) as mock_method:
        mock_method.return_value = __TESTS
        yield mock_method


@pytest.fixture
def __mock_log_warning():
    with patch(
        "scipion_testrunner.application.logger.Logger.log_warning"
    ) as mock_method:
        yield mock_method


@pytest.fixture
def __mock_get_test_config():
    with patch(
        "scipion_testrunner.configuration.test_config.get_test_config"
    ) as mock_method:
        mock_method.return_value = (__DATASETS, __SKIPPABLE, __INTERNAL_DEPENDENCIES)
        yield mock_method


@pytest.fixture
def __mock_remove_skippable_tests():
    with patch(
        "scipion_testrunner.domain.test_service.__remove_skippable_tests"
    ) as mock_method:
        yield mock_method


@pytest.fixture
def __mock_download_datasets():
    with patch(
        "scipion_testrunner.domain.handlers.scipion_handler.download_datasets"
    ) as mock_method:
        yield mock_method


@pytest.fixture
def __mock_run_tests():
    with patch(
        "scipion_testrunner.domain.handlers.scipion_handler.run_tests"
    ) as mock_method:
        mock_method.return_value = []
        yield mock_method


@pytest.fixture
def __mock_remove_gpu_tests():
    with patch(
        "scipion_testrunner.domain.test_service.__remove_gpu_tests"
    ) as mock_method:
        mock_method.side_effect = lambda tests, skippable_gpu, no_gpu: tests
        yield mock_method


@pytest.fixture
def __mock_remove_dependency_tests():
    with patch(
        "scipion_testrunner.domain.test_service.__remove_dependency_tests"
    ) as mock_method:
        mock_method.side_effect = lambda tests, skippable_dependency: tests
        yield mock_method


@pytest.fixture
def __mock_remove_other_tests():
    with patch(
        "scipion_testrunner.domain.test_service.__remove_other_tests"
    ) as mock_method:
        mock_method.side_effect = lambda tests, skippable_other: tests
        yield mock_method


@pytest.fixture
def __mock_log_skip_gpu_test():
    with patch(
        "scipion_testrunner.domain.test_service.__log_skip_gpu_test"
    ) as mock_method:
        yield mock_method


@pytest.fixture
def __mock_exists_python_module(request):
    with patch(
        "scipion_testrunner.domain.handlers.python_handler.exists_python_module"
    ) as mock_method:
        mock_method.return_value = request.param if hasattr(request, "param") else False
        yield mock_method


@pytest.fixture
def __mock_log_skip_dependency_test():
    with patch(
        "scipion_testrunner.domain.test_service.__log_skip_dependency_test"
    ) as mock_method:
        yield mock_method


@pytest.fixture
def __mock_log_skip_test():
    with patch("scipion_testrunner.domain.test_service.__log_skip_test") as mock_method:
        yield mock_method


@pytest.fixture
def __mock_remove_circular_dependencies():
    with patch(
        "scipion_testrunner.domain.test_service.__remove_circular_dependencies"
    ) as mock_method:
        mock_method.return_value = (__TESTS, __INTERNAL_DEPENDENCIES)
        yield mock_method


@pytest.fixture
def __mock_remove_unmet_internal_dependency_tests():
    with patch(
        "scipion_testrunner.domain.test_service.__remove_unmet_internal_dependency_tests"
    ) as mock_method:
        mock_method.return_value = (__TESTS, __INTERNAL_DEPENDENCIES)
        yield mock_method


@pytest.fixture
def __mock_generate_sorted_test_batches():
    with patch(
        "scipion_testrunner.domain.test_service.__generate_sorted_test_batches"
    ) as mock_method:
        mock_method.return_value = (__TESTS, [])
        yield mock_method


@pytest.fixture
def __mock_get_sorted_results():
    with patch(
        "scipion_testrunner.domain.test_service.__get_sorted_results"
    ) as mock_method:
        mock_method.return_value = {}
        yield mock_method


@pytest.fixture
def __mock_print():
    with patch("builtins.print") as mock_method:
        yield mock_method


@pytest.fixture
def __mock_log_result_summary():
    with patch(
        "scipion_testrunner.domain.test_service.__log_result_summary"
    ) as mock_method:
        yield mock_method


@pytest.fixture
def __mock_log_error():
    with patch("scipion_testrunner.application.logger.Logger.log_error") as mock_method:
        yield mock_method
