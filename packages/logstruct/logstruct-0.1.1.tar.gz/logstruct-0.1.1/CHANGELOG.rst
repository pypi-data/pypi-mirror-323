Changelog
=========

Upcoming
--------

...

v0.1.1 2025-01-24
-----------------

* Calling `StructuredLogger.exception` with an exception as ``exc_info`` will include the exception
  in the log instead of ``NoneType: None``. (`#1`_)

.. _#1: https://gitlab.com/karolinepauls/logstruct/-/issues/1

v0.1 2024-08-08
---------------

Initial release

* `logstruct.StructuredLogger`
* `logstruct.StructuredFormatter`
* Context: `logstruct.context_scope`, `logstruct.add_context`, `logstruct.remove_context`, etc.