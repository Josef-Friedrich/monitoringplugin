.. _intermediate-data-api:

Intermediate data API
=====================

The following classes allow to handle intermediate data that are used during the
plugin's execution in a structured way. Most of them are used by the
:mod:`mplugin` library itself to create objects which are passed into
code written by plugin authors. Other classes (like
:class:`~mplugin.metric.Metric`) are used by plugin authors to generate
intermediate data during :term:`acquisition` or :term:`evaluation` steps.

.. note::

   All classes that plugin authors typically need are imported directly into the
   :mod:`mplugin` name space. For example, use ::

      import mplugin
      # ...
      result = mplugin.Result(mplugin.Ok)

   to get a :class:`~mplugin.result.Result` instance.


mplugin.metric
-----------------------

.. automodule:: mplugin.metric
   :no-members:

.. autoclass:: Metric

   .. automethod:: __new__
   .. automethod:: __str__


mplugin.state
----------------------

.. automodule:: mplugin.state
   :no-members:

.. autoclass:: ServiceState

   .. automethod:: __str__
   .. automethod:: __int__

.. note::

   :class:`ServiceState` is not imported into the :mod:`mplugin`
   top-level name space since there is usually no need to access it directly.

.. autofunction:: mplugin.state.worst

State subclasses
^^^^^^^^^^^^^^^^

The state subclasses are singletons. Plugin authors should use the class
name (without parentheses) to access the instance. For example::

   state = mplugin.Critical


.. autoclass:: mplugin.state.Ok
.. autoclass:: mplugin.state.Warn
.. autoclass:: mplugin.state.Critical
.. autoclass:: mplugin.state.Unknown

Because these are implemented as classes, the `Warn` class cannot be named
`Warning`, or it would occlude the Python built-in exception class.

mplugin.performance
----------------------------

.. automodule:: mplugin.performance
   :no-members:

.. autoclass:: Performance

   .. automethod:: __new__
   .. automethod:: __str__


mplugin.range
----------------------

.. automodule:: mplugin.range
   :no-members:

.. autoclass:: Range

   .. automethod:: __new__
   .. automethod:: __str__
   .. automethod:: __repr__


mplugin.result
-----------------------

.. automodule:: mplugin.result
   :no-members:

.. autoclass:: Result

   .. automethod:: __new__
   .. automethod:: __str__

.. autoclass:: Results

   .. automethod:: __iter__
   .. automethod:: __len__
   .. automethod:: __getitem__
   .. automethod:: __contains__
