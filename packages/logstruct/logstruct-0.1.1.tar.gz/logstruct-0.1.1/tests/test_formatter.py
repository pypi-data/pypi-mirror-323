from __future__ import annotations

import inspect
import json
import logging
import time
import traceback
from dataclasses import replace
from io import StringIO
from pathlib import Path
from typing import Callable, NamedTuple

import pytest
from freezegun import freeze_time

import logstruct
from logstruct import (
    CONFIG_FORMATTED_MESSAGE,
    CONFIG_RAW_MESSAGE,
    LogField,
    StructuredFormatter,
    StructuredFormatterConfig,
    add_context,
    context_scope,
    make_friendly_dump_fn,
)

DIRPATH = str(Path(__file__).parent)


@pytest.fixture(params=[logging.getLogger, logstruct.getLogger], ids=["stdlib", "logstruct"])
def logger(request: pytest.FixtureRequest) -> logging.Logger | logstruct.StructuredLogger:
    get_logger: Callable[[str | None], logging.Logger | logstruct.StructuredLogger] = request.param

    name = request.node.function.__name__
    log = get_logger(f"test.{name}")
    log.setLevel(logging.DEBUG)
    log.parent = None
    log.handlers = [logging.StreamHandler(stream=StringIO())]
    return log


def current_line() -> int:
    caller_lineno = traceback.extract_stack()[-2].lineno
    assert caller_lineno is not None
    return caller_lineno


def log_lines(logger: logging.Logger | logstruct.StructuredLogger) -> list[dict[str, object]]:
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    stream = handler.stream
    assert isinstance(stream, StringIO)

    stream.seek(0)
    return [json.loads(line.replace(DIRPATH, "")) for line in stream]


def format_exception(exc: BaseException) -> str:
    return (
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        .replace(DIRPATH, "")
        .rstrip("\n")
    )


class ExpectedLogContents(NamedTuple):
    """Expected details of sent test logs."""

    info_log_line: int
    warning_log_line: int
    error_log_line: int
    exception_log_line: int
    stack_info_log_line: int
    formatted_exception: str
    expected_stack: str


def send_logs(logger: logging.Logger | logstruct.StructuredLogger) -> ExpectedLogContents:
    line = current_line()
    logger.info("An info message")
    logger.warning("An info message with positional args: %r", "abc")
    logger.error("An info message with data", extra={"log": "struct", "unrepresentable": {1, 2, 3}})
    try:
        print(1 / 0)
    except ZeroDivisionError as exc:
        logger.exception("Division error")
        formatted_exception = format_exception(exc)

    stack_info_log_line = current_line() + 1
    logger.critical("A critical message with stack info", stack_info=True)

    this_frame = inspect.currentframe()
    assert this_frame is not None
    caller_frame = this_frame.f_back
    expected_stack = (
        "Stack (most recent call last):\n"
        + "".join(traceback.format_stack(caller_frame)).replace(DIRPATH, "")
        + f"""\
  File "/test_formatter.py", line {stack_info_log_line}, in send_logs
    logger.critical("A critical message with stack info", stack_info=True)"""
    )
    return ExpectedLogContents(
        info_log_line=line + 1,
        warning_log_line=line + 2,
        error_log_line=line + 3,
        exception_log_line=line + 7,
        stack_info_log_line=stack_info_log_line,
        formatted_exception=formatted_exception,
        expected_stack=expected_stack,
    )


@freeze_time("2024-06-30")
def test_default_config(logger: logging.Logger | logstruct.StructuredLogger) -> None:
    formatter = StructuredFormatter()
    formatter.converter = time.gmtime
    logger.handlers[0].formatter = formatter

    expected_logs = send_logs(logger)

    assert log_lines(logger) == [
        {
            "func": "send_logs",
            "level": "INFO",
            "line": expected_logs.info_log_line,
            "logger": "test.test_default_config",
            "message": "An info message",
            "time": "2024-06-30 00:00:00,000",
        },
        {
            "func": "send_logs",
            "level": "WARNING",
            "line": expected_logs.warning_log_line,
            "logger": "test.test_default_config",
            "message": "An info message with positional args: 'abc'",
            "time": "2024-06-30 00:00:00,000",
        },
        {
            "func": "send_logs",
            "level": "ERROR",
            "line": expected_logs.error_log_line,
            "logger": "test.test_default_config",
            "message": "An info message with data",
            "log": "struct",
            "time": "2024-06-30 00:00:00,000",
            "unrepresentable": "{1, 2, 3}",
        },
        {
            "exc_text": expected_logs.formatted_exception,
            "func": "send_logs",
            "level": "ERROR",
            "line": expected_logs.exception_log_line,
            "logger": "test.test_default_config",
            "message": "Division error",
            "time": "2024-06-30 00:00:00,000",
        },
        {
            "func": "send_logs",
            "level": "CRITICAL",
            "line": expected_logs.stack_info_log_line,
            "logger": "test.test_default_config",
            "message": "A critical message with stack info",
            "time": "2024-06-30 00:00:00,000",
            "stack_info": expected_logs.expected_stack,
        },
    ]


@freeze_time("2024-06-30")
def test_dev_friendly_format(logger: logging.Logger | logstruct.StructuredLogger) -> None:
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    formatter = StructuredFormatter(
        structured_formatter_config=StructuredFormatterConfig(
            dumps_fn=make_friendly_dump_fn(),
        )
    )
    formatter.converter = time.gmtime
    handler.formatter = formatter

    expected_logs = send_logs(logger)

    expected_output = f"""\
2024-06-30 00:00:00,000 INFO     test.test_dev_friendly_format:send_logs:{expected_logs.info_log_line} \
An info message
2024-06-30 00:00:00,000 WARNING  test.test_dev_friendly_format:send_logs:{expected_logs.warning_log_line} \
An info message with positional args: 'abc'
2024-06-30 00:00:00,000 ERROR    test.test_dev_friendly_format:send_logs:{expected_logs.error_log_line} \
An info message with data {{"log": "struct", "unrepresentable": "{{1, 2, 3}}"}}
2024-06-30 00:00:00,000 ERROR    test.test_dev_friendly_format:send_logs:{expected_logs.exception_log_line} \
Division error
{expected_logs.formatted_exception}
2024-06-30 00:00:00,000 CRITICAL test.test_dev_friendly_format:send_logs:{expected_logs.stack_info_log_line} \
A critical message with stack info
{expected_logs.expected_stack}
"""
    assert isinstance(handler.stream, StringIO)
    assert handler.stream.getvalue().replace(DIRPATH, "") == expected_output


@freeze_time("2024-06-30")
def test_raw_message_config(logger: logging.Logger) -> None:
    formatter = StructuredFormatter(structured_formatter_config=CONFIG_RAW_MESSAGE)
    formatter.converter = time.gmtime
    logger.handlers[0].formatter = formatter

    line = current_line()
    logger.info("An info message with positional args: %r", "abc")

    assert log_lines(logger) == [
        {
            "func": "test_raw_message_config",
            "level": "INFO",
            "line": line + 1,
            "logger": "test.test_raw_message_config",
            "message": "An info message with positional args: %r",
            "positional_args": ["abc"],
            "time": "2024-06-30 00:00:00,000",
        },
    ]


@freeze_time("2024-06-30")
def test_uses_time_false(logger: logging.Logger) -> None:
    config = replace(CONFIG_FORMATTED_MESSAGE, uses_time=False)
    logger.handlers[0].formatter = StructuredFormatter(structured_formatter_config=config)

    line = current_line()
    logger.info("An info message without a timestamp")

    assert "time" not in log_lines(logger)[0]
    assert log_lines(logger) == [
        {
            "func": "test_uses_time_false",
            "level": "INFO",
            "line": line + 1,
            "logger": "test.test_uses_time_false",
            "message": "An info message without a timestamp",
        },
    ]


@freeze_time("2024-06-30")
def test_custom_attribute_mapping(logger: logging.Logger) -> None:
    config = StructuredFormatterConfig(
        log_fields=(
            LogField("asctime", "ts", bool),
            LogField("name", "log"),
            LogField("levelname", "lvl"),
            LogField("pathname", "file"),
            LogField("module", "mod"),
            LogField("funcName", "fn"),
            LogField("lineno", "no"),
            LogField("message", "event"),
            LogField("exc_text", "exception", bool),
            LogField("stack_info", "stack", bool),
        ),
    )
    formatter = StructuredFormatter(structured_formatter_config=config)
    formatter.converter = time.gmtime
    logger.handlers[0].formatter = formatter

    line = current_line()
    logger.info("An info message")
    try:
        print(1 / 0)
    except ZeroDivisionError as exc:
        logger.exception("Division error")
        formatted_exception = format_exception(exc)

    assert log_lines(logger) == [
        {
            "fn": "test_custom_attribute_mapping",
            "lvl": "INFO",
            "no": line + 1,
            "log": "test.test_custom_attribute_mapping",
            "event": "An info message",
            "mod": "test_formatter",
            "file": "/test_formatter.py",
            "ts": "2024-06-30 00:00:00,000",
        },
        {
            "exception": formatted_exception,
            "fn": "test_custom_attribute_mapping",
            "lvl": "ERROR",
            "no": line + 5,
            "log": "test.test_custom_attribute_mapping",
            "event": "Division error",
            "mod": "test_formatter",
            "file": "/test_formatter.py",
            "ts": "2024-06-30 00:00:00,000",
        },
    ]


def test_extra_precedence_over_record(logger: logging.Logger) -> None:
    logger.handlers[0].formatter = StructuredFormatter()

    logger.info("Message")
    line = log_lines(logger)[-1]
    assert line["logger"] == logger.name

    logger.info("Message", extra={"logger": "extra"})
    line = log_lines(logger)[-1]
    assert line["logger"] == "extra"


def test_context_vars_enabled(logger: logging.Logger) -> None:
    logger.handlers[0].formatter = StructuredFormatter()

    def log_line() -> dict[str, object]:
        logger.info("Message")
        return log_lines(logger)[-1]

    with context_scope(x=11):
        line = log_line()
        assert line["x"] == 11

        add_context(y=22)
        line = log_line()
        assert line["x"] == 11
        assert line["y"] == 22

    line = log_line()
    assert "x" not in line
    assert "y" not in line


def test_context_vars_disabled(logger: logging.Logger) -> None:
    config = replace(CONFIG_FORMATTED_MESSAGE, get_context_fn=None)
    logger.handlers[0].formatter = StructuredFormatter(structured_formatter_config=config)

    with context_scope(x=1):
        logger.info("Message")
        [line] = log_lines(logger)
        assert "x" not in line


def test_context_vars_custom(logger: logging.Logger) -> None:
    context: dict[str, object] = {}

    def get_context_fn() -> dict[str, object]:
        return context

    config = replace(CONFIG_FORMATTED_MESSAGE, get_context_fn=get_context_fn)
    logger.handlers[0].formatter = StructuredFormatter(structured_formatter_config=config)

    context["q"] = "p"

    logger.info("Message")
    [line] = log_lines(logger)
    assert line["q"] == "p"


def test_context_precedence(logger: logging.Logger) -> None:
    logger.handlers[0].formatter = StructuredFormatter()

    logger.info("Message")
    line = log_lines(logger)[-1]
    assert line["logger"] == logger.name

    with context_scope(logger="context"):
        logger.info("Message")
        line = log_lines(logger)[-1]
        assert line["logger"] == "context", "Context should take precedence over record attrs"

    with context_scope(key="context"):
        logger.info("Message", extra={"key": "extra"})
        line = log_lines(logger)[-1]
        assert line["key"] == "extra", "Extra should take precedence over context"


@pytest.mark.parametrize("method", ["debug", "info", "warning", "error", "exception"])
def test_exc_info_exception(logger: logging.Logger, method: str) -> None:
    logger.handlers[0].formatter = StructuredFormatter()
    getattr(logger, method)("message", exc_info=ValueError("oops"))
    assert log_lines(logger)[-1]["exc_text"] == "ValueError: oops"
