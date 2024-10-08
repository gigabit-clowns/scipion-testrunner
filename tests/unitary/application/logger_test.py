from unittest.mock import patch

import pytest

from scipion_testrunner.application.logger import Logger

__TEST_STRING = "Test print"
__GREEN = "<GREEN>"
__YELLOW = "<YELLOW>"
__RED = "<RED>"
__BLUE = "<BLUE>"
__END_FORMAT = "<END_FORMAT>"


def test_logger_is_called_with_expected_text_when_logging_to_stdout(__mock_print):
    logger = Logger()
    logger(__TEST_STRING)
    __mock_print.assert_called_once_with(__TEST_STRING, flush=True)


@pytest.mark.parametrize(
    "color_method",
    [
        pytest.param(Logger.green),
        pytest.param(Logger.yellow),
        pytest.param(Logger.red),
        pytest.param(Logger.blue),
    ],
)
def test_logger_is_called_with_expected_formatted_text_when_logging_to_stdout(
    color_method, __mock_print
):
    logger = Logger()
    logger(color_method(logger, __TEST_STRING))
    __mock_print.assert_called_once_with(
        color_method(logger, __TEST_STRING), flush=True
    )


def test_logger_is_called_with_expected_text_when_logging_warning(__mock_print):
    logger = Logger()
    logger.log_warning(__TEST_STRING)
    __mock_print.assert_called_with(logger.yellow(__TEST_STRING), flush=True)


def test_logger_is_called_with_expected_text_when_logging_error(
    __mock_print, __mock_exit
):
    logger = Logger()
    logger.log_error(__TEST_STRING)
    __mock_print.assert_called_with(logger.red(__TEST_STRING), flush=True)


@pytest.mark.parametrize(
    "color_method,starting_formatting_character",
    [
        pytest.param(Logger.green, __GREEN),
        pytest.param(Logger.yellow, __YELLOW),
        pytest.param(Logger.red, __RED),
        pytest.param(Logger.blue, __BLUE),
    ],
)
def test_returns_expected_formatted_text(
    color_method, starting_formatting_character, __mock_logger_format_attributes
):
    logger = Logger()
    assert (
        color_method(logger, __TEST_STRING)
        == f"{starting_formatting_character}{__TEST_STRING}{__END_FORMAT}"
    ), "Color format has not been properly set."


@pytest.fixture
def __mock_print():
    with patch("builtins.print") as mock_method:
        yield mock_method


@pytest.fixture
def __mock_exit():
    with patch("sys.exit") as mock_method:
        yield mock_method


@pytest.fixture
def __mock_logger_format_attributes():
    with patch.object(Logger, "_Logger__GREEN", __GREEN) as mock_green, patch.object(
        Logger, "_Logger__YELLOW", __YELLOW
    ) as mock_yellow, patch.object(
        Logger, "_Logger__RED", __RED
    ) as mock_red, patch.object(
        Logger, "_Logger__BLUE", __BLUE
    ) as mock_blue, patch.object(
        Logger, "_Logger__END_FORMAT", __END_FORMAT
    ) as mock_end_format:
        yield mock_green, mock_yellow, mock_red, mock_blue, mock_end_format
