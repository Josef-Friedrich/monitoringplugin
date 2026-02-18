.. _core-api:

Core API
========

The core API consists of all functions and classes which are called in
a plugin's `main` function. A typical main function is decorated with
:func:`~monitoringplugin.runtime.guarded` and creates a
:class:`~monitoringplugin.check.Check` object. The check instance is fed with
instances of :class:`~monitoringplugin.resource.Resource`,
:class:`~monitoringplugin.context.Context`, or
:class:`~monitoringplugin.summary.Summary` (respective custom subclasses). Finally,
control is passed to the check's :meth:`~monitoringplugin.check.Check.main` method.

.. note::

   All classes that plugin authors typically need are imported into the
   :mod:`monitoringplugin` name space. For example, use ::

      import monitoringplugin
      # ...
      check = monitoringplugin.Check()

   to get a :class:`~monitoringplugin.check.Check` instance.


monitoringplugin.check
----------------------

.. automodule:: monitoringplugin.check
   :no-members:

.. autoclass:: Check
   :no-index:

   .. automethod:: __call__

   .. attribute:: name

      Short name which is used to prefix the check's status output (as commonly
      found in plugins shipped with Nagios). It defaults to the uppercased class
      name of the first resource added. However, plugin authors may override
      this by assigning an user-defined name. If this attribute is None, status
      output will not be prefixed with a check name.

   .. attribute:: results

      :class:`~monitoringplugin.result.Results` container that allows accessing the
      :class:`~monitoringplugin.result.Result` objects generated during the
      evaluation.

.. topic:: Example: Skeleton main function

   The following pseudo code outlines how :class:`Check` is typically used in
   the main function of a plugin::

      def main():
         check = monitoringplugin.Check(MyResource1(...), MyResource2(...),
                                    MyContext1(...), MyContext2(...),
                                    MySummary(...))
         check.main()


monitoringplugin.resource
-------------------------

.. automodule:: monitoringplugin.resource
   :no-members:

.. autoclass:: Resource


monitoringplugin.context
------------------------

.. automodule:: monitoringplugin.context
   :no-members:

.. autoclass:: Context

.. autoclass:: ScalarContext

.. topic:: Example ScalarContext usage

   Configure a ScalarContext with warning and critical ranges found in
   ArgumentParser's result object `args` and add it to a check::

      c = Check(..., ScalarContext('metric', args.warning, args.critical), ...)


monitoringplugin.summary
------------------------

.. automodule:: monitoringplugin.summary
   :no-members:

.. autoclass:: Summary


monitoringplugin.runtime
------------------------

.. automodule:: monitoringplugin.runtime
   :no-members:

.. autofunction:: guarded(*args, verbose=None)

.. vim: set spell spelllang=en:
