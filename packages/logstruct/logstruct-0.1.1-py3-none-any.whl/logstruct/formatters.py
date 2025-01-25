"""A structured logging formatter compatible with standard library logging.

A replacement for structlog, at 1% the headache structlog causes. Does not get in the way with logging, its
integrations (like Sentry). Can be assigned to any handler.

LogRecords are turned into dicts and serialised. The ``extra`` dict passed to log calls is included in the
created dict.

JSON isn't mandatory. Any str -> dict function can be passed to the config.
"""

from __future__ import annotations

import functools
import json
import logging
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Optional, cast

from logstruct.context import get_context


@functools.cache
def _get_standard_logrecord_keys() -> set[str]:
    return set(logging.makeLogRecord({}).__dict__.keys()) | {"message", "asctime"}


def _find_extras_in_logrecord(record: logging.LogRecord) -> dict[str, Any]:
    return {k: v for k, v in record.__dict__.items() if k not in _get_standard_logrecord_keys()}


@dataclass(frozen=True)
class LogField:
    """A mapping of a single LogRecord attribute to its corresponding output data key.

    May contain an optional inclusion condition.
    """

    log_record_attr: str
    struct_key: str
    condition: Callable[[Any], bool] | None = None


@dataclass(frozen=True)
class StructuredFormatterConfig:
    """Logrecord formatter config.

    Can be used to reflect any LogRecord attribute as a key-value of a dict, later passed to ``dumps_fn``.

    A major difference from structlog is that by default the log message goes to the "message" key rather than
    "event".
    """

    format_message: bool = True
    """If True, take the message from ``record.getMessage()`` otherwise ``record.msg`` (unformatted)."""

    uses_time: bool = True

    log_fields: Sequence[LogField] = (
        LogField("asctime", "time", bool),
        LogField("name", "logger"),
        LogField("levelname", "level"),
        # Path and module not included by default because they are typically redundant with the logger name.
        # LogField("pathname", "path"),
        # LogField("module", "module"),
        LogField("funcName", "func"),
        LogField("lineno", "line"),
        # Message will be computed by the formatter before mapping if `format_message` is True
        LogField("message", "message"),
        LogField("exc_text", "exc_text", bool),
        LogField("stack_info", "stack_info", bool),
    )

    get_context_fn: Callable[[], dict[str, object]] | None = get_context
    dumps_fn: Callable[..., str] = functools.partial(json.dumps, default=repr)
    """
    By default ``dumps_fn`` is :py:func:`json.dumps` which will apply :py:func:`repr` to otherwise
    unserialisable objects, however any serialiser func can be used.
    """


def make_friendly_dump_fn(
    log_fields: Sequence[LogField] = StructuredFormatterConfig.log_fields,
    dumps_fn: Callable[..., str] = StructuredFormatterConfig.dumps_fn,
    colours: bool = False,
) -> Callable[[dict[str, object]], str]:
    """Build a function serialising structured data in a developer-friendly way.

    A typical message looks like:

    .. code::

        2024-08-07 23:10:06,605 INFO     __main__:<module>:35 A message {"key": "val"}

    This is not meant to be the only way to serialise logged data in development. Users can supply their own
    friendly dump function.
    """
    record_attr_to_key = {f.log_record_attr: f.struct_key for f in log_fields}

    level_key = record_attr_to_key.get("levelname")
    logger_name_key = record_attr_to_key.get("name")
    line_key = record_attr_to_key.get("lineno")
    time_key = record_attr_to_key.get("asctime")
    func_key = record_attr_to_key.get("funcName")
    message_key = record_attr_to_key.get("message")
    exc_text_key = record_attr_to_key.get("exc_text")
    stack_info_key = record_attr_to_key.get("stack_info")

    if colours:
        levels = {
            "DEBUG": "\033[0;1m",
            "INFO": "\033[92;1m",
            "WARNING": "\033[93;1m",
            "ERROR": "\033[91;1m",
            "CRITICAL": "\033[101;1m",
        }
        bold = "\033[1m"
        reset = "\033[0m"
    else:
        levels = {}
        bold = ""
        reset = ""

    def friendly_dump_fn(
        data: dict[str, object],
    ) -> str:
        """Serialise data in a developer-friendly way."""
        d = cast(dict[Optional[str], object], data)  # cast does not with with str | None in place of Optional

        level = d.pop(level_key, "<no level>")
        logger_name = d.pop(logger_name_key, "<no name>")
        line = d.pop(line_key, "<no line>")
        time = d.pop(time_key, "<no time>")
        func = d.pop(func_key, "<no func>")
        message = d.pop(message_key, "<no message>")
        exc_text = d.pop(exc_text_key, "")
        stack_info = d.pop(stack_info_key, "")

        newline = "\n"
        level_format = levels.get(level, "") if isinstance(level, str) else ""
        return (
            f"{time} {level_format}{level:8}{reset} {bold}{logger_name}{reset}:{func}:{line}"
            f"{' ' if message else ''}{bold}{message}{reset}"
            f"{' ' if data else ''}{dumps_fn(data) if data else ''}"
            f"{newline if exc_text else ''}{exc_text}"
            f"{newline if stack_info else ''}{stack_info}"
        )

    return friendly_dump_fn


CONFIG_FORMATTED_MESSAGE = StructuredFormatterConfig()
CONFIG_RAW_MESSAGE = StructuredFormatterConfig(
    format_message=False,
    log_fields=tuple(CONFIG_FORMATTED_MESSAGE.log_fields) + (LogField("args", "positional_args", bool),),
)

_FormatStyle = Literal["%", "{", "$"]


class StructuredFormatter(logging.Formatter):
    """A logging formatter that turns LogRecords into structured data."""

    __config: StructuredFormatterConfig

    if TYPE_CHECKING:
        if sys.version_info >= (3, 10):

            def __init__(  # noqa: D107
                self,
                fmt: str | None = None,
                datefmt: str | None = None,
                style: _FormatStyle = "%",
                validate: bool = True,
                *,
                defaults: Mapping[str, Any] | None = None,
                structured_formatter_config: StructuredFormatterConfig | None = None,
            ) -> None: ...

        else:

            def __init__(  # noqa: D107
                self,
                fmt: str | None = None,
                datefmt: str | None = None,
                style: _FormatStyle = "%",
                validate: bool = True,
                *,
                structured_formatter_config: StructuredFormatterConfig | None = None,
            ) -> None: ...

    else:

        def __init__(
            self,
            *args,
            structured_formatter_config: StructuredFormatterConfig | None = None,
            **kwargs,
        ) -> None:
            """Initialise the formatter and save config specific to StructuredFormatter."""
            super().__init__(*args, **kwargs)
            self.__config = (
                structured_formatter_config
                if structured_formatter_config is not None
                else CONFIG_FORMATTED_MESSAGE
            )

    def usesTime(self) -> bool:
        """Check if "asctime" should be assigned to the log record.

        The standard formatter checks if "asctime" is used in the log style. We don't use the
        log styles.
        """
        return self.__config.uses_time

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record according to the config.

        Key-value pairs are discovered in the log record, the context (unless disabled), and the extra dict
        passed to the log call. They are merged into a single dict with precedence: extras, context, record.

        Mostly a clone of ``logging.Formatter.format`` but writes structured data. The ``self.formatMessage``,
        method, which normally produces a log line prefix, is not called since record attributes are included
        as data instead. The message itself is still formatted by calling ``record.getMessage()`` if enabled
        by the config.

        The reason for mutating the record is compatibility with `logging.Formatter` which does the same
        thing.
        """
        config = self.__config

        # Unlike logging, we can disable positional argument substitution
        if config.format_message:
            record.message = record.getMessage()
        else:
            record.message = record.msg

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        # this block is copy-pasted from logging, with SIM102 fixed.
        if record.exc_info and not record.exc_text:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            # logging also mutates it, blame them
            record.exc_text = self.formatException(record.exc_info)

        structured_data = {}
        for record_attr_map in config.log_fields:
            val = getattr(record, record_attr_map.log_record_attr, None)
            if record_attr_map.condition is None or record_attr_map.condition(val):
                structured_data[record_attr_map.struct_key] = val

        if config.get_context_fn is not None:
            structured_data.update(config.get_context_fn())

        structured_data.update(_find_extras_in_logrecord(record))

        return config.dumps_fn(structured_data)
