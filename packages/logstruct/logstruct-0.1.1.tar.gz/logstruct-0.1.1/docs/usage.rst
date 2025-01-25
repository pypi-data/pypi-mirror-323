Usage
=====

..
    WARNING! The program-output directive caches the output based on the command. `make clean` is needed when
    demos change to see the changes locally.


Setup
-----

.. testsetup::

   import sys
   import logging
   import logstruct

   # Use sys.stdout so that doctests capture the logs
   logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

``logstruct`` provides a formatter that formats all log records from standard library `logging.Logger` or its own `StructuredLogger <logstruct.StructuredLogger>` as JSON.

.. testcode::

   logging.basicConfig(level=logging.DEBUG)
   logging.root.handlers[0].formatter = logstruct.StructuredFormatter()

   logging.getLogger("stdlib-logger").info("hello world")

.. testoutput::

   {"time": "...", "logger": "stdlib-logger", "level": "INFO", ..., "message": "hello world"}

.. _logger_usage:

Structured data
---------------

`StructuredLogger <logstruct.StructuredLogger>` is a replacement for the standard library
`logging.Logger` with an almost identical API. The key difference is that additional keyword
arguments provided to logging functions are automatically included in structured output.

.. testcode::

   logger = logstruct.getLogger(__name__)

   logger.info("hello", request_id=1234, user="black_knight")

.. testoutput::

   {..., "level": "INFO", ..., "message": "hello", "request_id": 1234, "user": "black_knight"}

This works for all logging levels.

.. testcode::
   :hide:

   logger.setLevel(logging.DEBUG)

.. testcode::

   logger.debug("good to know", request_id=1234)
   logger.warning("take a look", request_id=1234)
   logger.error("uh-oh", request_id=1234)

.. testoutput::

   {..., "level": "DEBUG", ..., "message": "good to know", "request_id": 1234}
   {..., "level": "WARNING", ..., "message": "take a look", "request_id": 1234}
   {..., "level": "ERROR", ..., "message": "uh-oh", "request_id": 1234}

Alternatively, structured data can be passed as a dictionary in the ``extra`` parameter:

.. testcode::

   logger.info("hello", extra={"request_id": 1234, "user": "black_knight"})

.. testoutput::

   {..., "message": "hello", "request_id": 1234, "user": "black_knight"}

Exception logging
^^^^^^^^^^^^^^^^^

Similar to `logging.Logger`, you can include exception information using the ``exc_info`` parameter:

.. testcode::

   logger.error("uh-oh", exc_info=ValueError("wrong value"), request_id=1234)

.. testoutput::

   {..., "message": "uh-oh", "exc_text": "ValueError: wrong value", "request_id": 1234}

The currently handled exception is automatically captured if ``exc_info`` is true or if
`logger.exception <logstruct.StructuredLogger.exception>` is called.

.. testcode::

   try:
       x = 1 / 0
   except ZeroDivisionError:
       logger.debug("debug", exc_info=True, request_id=1234)
       logger.exception("error", request_id=1234)

.. testoutput::

   {..., "level": "DEBUG",... "message": "debug", "exc_text": "Traceback ...ZeroDivisionError: division by zero", "request_id": 1234}
   {..., "level": "ERROR",... "message": "error", "exc_text": "Traceback ...ZeroDivisionError: division by zero", "request_id": 1234}

Logging config file (YAML)
--------------------------

.. literalinclude:: ../example_config.yaml
   :caption: example_config.yaml
   :language: yaml

.. literalinclude:: ../demo_dict_config.py
   :caption: demo_dict_config.py
   :language: py

.. program-output:: ../demo_dict_config.py
   :caption: log output


Logging config file (ini)
-------------------------

.. literalinclude:: ../example_config.ini
   :caption: example_config.ini
   :language: ini

.. literalinclude:: ../demo_file_config.py
   :caption: demo_file_config.py
   :language: py

.. program-output:: ../demo_file_config.py
   :caption: log output

.. _context_usage:

Context variables
-----------------

Logstruct context variables are meant to contain data relevant to the current operation, like
message ID, request path, user ID, job name, job ID, etc. Once set, they are shared by all
subsequent logs until they are unset.

Context variables are automatically incorporated in produced structured logs but they can be overridden by
keyword args directly passed to log calls. Context variables are implemented with `contextvars.Context`
which makes them local to the current thread, asyncio task, or gevent task. Context variables are automatically inherited by child tasks but not by spawned threads.

.. testcleanup::

   logstruct.clear_scope()

You can use `context_scope <logstruct.context_scope>` to add contextual information to all log
records within the scope.

.. testcode::


   with logstruct.context_scope(request_id="1234"):
       logger.info("has context", user="abc")

   logger.info("scope ended")

.. testoutput::

   {..., "message": "has context", "request_id": "1234", "user": "abc"}
   {..., "message": "scope ended"}

Contexts can be nested. Inner scopes shadow data from outer scopes.

.. testcode::

   with logstruct.context_scope(outer="outer", redefined="outer"):
       with logstruct.context_scope(inner="inner", redefined="inner"):
           logger.info("inner context")

.. testoutput::

   {..., "message": "inner context", "inner": "inner", "redefined": "inner", "outer": "outer"}


You can modify the current context with `add_context <logstruct.add_context>`, `remove_context
<logstruct.remove_context>`, and `clear_scope <logstruct.clear_scope>`.

.. testcode::

   logstruct.add_context(request_id="1234")
   logstruct.add_context(user="abc")
   logger.info("has context")

   logstruct.remove_context("user")
   logger.info("only request_id")

   logstruct.clear_scope()
   logger.info("no context")

.. testoutput::

   {..., "message": "has context", "request_id": "1234", "user": "abc"}
   {..., "message": "only request_id", "request_id": "1234"}
   {..., "message": "no context"}

Modifications only apply to the current scope. Once the scope ends, all
modifications are lost.

.. testcode::

   with logstruct.context_scope(request_id="1234"):
     logstruct.add_context(user="abc")
     logger.info("modified")

   logger.info("unmodified")

.. testoutput::

   {..., "message": "modified", "request_id": "1234", "user": "abc"}
   {..., "message": "unmodified"}

.. _formatter_usage:

Highly customised config
------------------------

.. literalinclude:: ../demo_custom.py
   :language: py

.. program-output::  ../demo_custom.py
   :caption: log output

.. _dev_mode_logging:

Development mode logging
------------------------

In this demo the ``DEBUG`` env var set to a non-empty value makes logs formatted in a developer-friendly way,
but unlike the default formatter, will include the ``extra`` dictionary, where our log call key-values go.

.. literalinclude:: ../demo_dev_mode.py
   :language: py

.. program-output:: sh -c 'DEBUG=1 ../demo_dev_mode.py'
   :caption: DEBUG=1

.. program-output:: ../demo_dev_mode.py
   :caption: DEBUG not set
   :shell:
