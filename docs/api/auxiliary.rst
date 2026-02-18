.. _auxiliary-classes:

Auxiliary Classes
=================

mplugin's auxiliary classes are not strictly required to write checks, but
simplify common tasks and provide convenient access to functionality that is
regularly needed by plugin authors.

.. note::

   All classes that plugin authors typically need are imported directly into the
   :mod:`mplugin` name space. For example, use ::

      import mplugin
      # ...
      with mplugin.Cookie(path) as cookie:
         # ...

   to get a cookie.


mplugin.cookie
-----------------------

.. automodule:: mplugin.cookie
   :no-members:

.. autoclass:: Cookie

   .. automethod:: __enter__

.. topic:: Cookie example

   Increment a connection count saved in the cookie by `self.new_conns`::

      with mplugin.Cookie(self.statefile) as cookie:
         cookie['connections'] = cookie.get('connections', 0) + self.new_conns

   Note that the new content is committed automatically when exiting the `with`
   block.


mplugin.logtail
------------------------

.. automodule:: mplugin.logtail
   :no-members:

.. autoclass:: LogTail

   .. automethod:: __enter__

.. topic:: LogTail example

   Calls `process()` for each new line in a log file::

      cookie = mplugin.Cookie(self.statefile)
      with mplugin.LogTail(self.logfile, cookie) as newlines:
         for line in newlines:
            process(line.decode())

.. vim: set spell spelllang=en:
