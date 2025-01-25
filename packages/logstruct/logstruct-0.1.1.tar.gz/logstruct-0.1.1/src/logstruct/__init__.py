"""Structured logging formatter."""

from __future__ import annotations

try:
    from logstruct._version import __version__, __version_tuple__
except ImportError:
    __version__ = "develop"
    __version_tuple__ = (0, 0, 0)

from logstruct.context import add_context, clear_scope, context_scope, get_context, remove_context
from logstruct.formatters import (
    CONFIG_FORMATTED_MESSAGE,
    CONFIG_RAW_MESSAGE,
    LogField,
    StructuredFormatter,
    StructuredFormatterConfig,
    make_friendly_dump_fn,
)
from logstruct.logger import StructuredLogger, getLogger

__all__ = [
    "__version__",
    "__version_tuple__",
    "LogField",
    "StructuredFormatter",
    "StructuredFormatterConfig",
    "make_friendly_dump_fn",
    "CONFIG_FORMATTED_MESSAGE",
    "CONFIG_RAW_MESSAGE",
    "StructuredLogger",
    "getLogger",
    "add_context",
    "clear_scope",
    "context_scope",
    "get_context",
    "remove_context",
]
