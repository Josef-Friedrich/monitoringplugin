.. _intermediate-data-api:

Intermediate data API
=====================

The following classes allow to handle intermediate data that are used during the
plugin's execution in a structured way. Most of them are used by the
:mod:`monitoringplugin` library itself to create objects which are passed into
code written by plugin authors. Other classes (like
:class:`~monitoringplugin.metric.Metric`) are used by plugin authors to generate
intermediate data during :term:`acquisition` or :term:`evaluation` steps.

.. note::

   All classes that plugin authors typically need are imported directly into the
   :mod:`monitoringplugin` name space. For example, use ::

      import monitoringplugin
      # ...
      result = monitoringplugin.Result(monitoringplugin.Ok)

   to get a :class:`~monitoringplugin.result.Result` instance.


monitoringplugin.metric
-----------------------

.. automodule:: monitoringplugin.metric
   :no-members:

.. autoclass:: Metric

   .. automethod:: __new__
   .. automethod:: __str__


monitoringplugin.state
----------------------

.. automodule:: monitoringplugin.state
   :no-members:

.. autoclass:: ServiceState

   .. automethod:: __str__
   .. automethod:: __int__

.. note::

   :class:`ServiceState` is not imported into the :mod:`monitoringplugin`
   top-level name space since there is usually no need to access it directly.

.. autofunction:: monitoringplugin.state.worst

State subclasses
^^^^^^^^^^^^^^^^

The state subclasses are singletons. Plugin authors should use the class
name (without parentheses) to access the instance. For example::

   state = monitoringplugin.Critical


.. autoclass:: monitoringplugin.state.Ok
.. autoclass:: monitoringplugin.state.Warn
.. autoclass:: monitoringplugin.state.Critical
.. autoclass:: monitoringplugin.state.Unknown

Because these are implemented as classes, the `Warn` class cannot be named
`Warning`, or it would occlude the Python built-in exception class.

monitoringplugin.performance
----------------------------

.. automodule:: monitoringplugin.performance
   :no-members:

.. autoclass:: Performance

   .. automethod:: __new__
   .. automethod:: __str__


monitoringplugin.range
----------------------

.. automodule:: monitoringplugin.range
   :no-members:

.. autoclass:: Range

   .. automethod:: __new__
   .. automethod:: __str__
   .. automethod:: __repr__


monitoringplugin.result
-----------------------

.. automodule:: monitoringplugin.result
   :no-members:

.. autoclass:: Result

   .. automethod:: __new__
   .. automethod:: __str__

.. autoclass:: Results

   .. automethod:: __iter__
   .. automethod:: __len__
   .. automethod:: __getitem__
   .. automethod:: __contains__
