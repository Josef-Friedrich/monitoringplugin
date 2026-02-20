from __future__ import annotations

import functools
import importlib
import json
import os
import typing
from collections import UserDict
from importlib import metadata
from io import BufferedIOBase
from tempfile import TemporaryFile
from types import TracebackType
from typing import Any, Iterator, Optional, Union

from typing_extensions import Self

__version__: str = metadata.version("mplugin")


# error.py

"""Exceptions with special meanings for mplugin."""


class CheckError(RuntimeError):
    """Abort check execution.

    This exception should be raised if it becomes clear for a plugin
    that it is not able to determine the system status. Raising this
    exception will make the plugin display the exception's argument and
    exit with an UNKNOWN (3) status.
    """

    pass


class Timeout(RuntimeError):
    """Maximum check run time exceeded.

    This exception is raised internally by mplugin if the check's
    run time takes longer than allowed. Check execution is aborted and
    the plugin exits with an UNKNOWN (3) status.
    """

    pass


# state.py

"""Classes  to represent check outcomes.

This module defines :class:`ServiceState` which is the abstract base class
for check outcomes. The four states defined by the :term:`Nagios plugin API`
are represented as singleton subclasses.

Note that the *warning* state is defined by the :class:`Warn` class. The
class has not been named `Warning` to avoid being confused with the
built-in Python exception of the same name.
"""


def worst(states: list["ServiceState"]) -> "ServiceState":
    """Reduce list of *states* to the most significant state."""
    return functools.reduce(lambda a, b: a if a > b else b, states, ok)


class ServiceState:
    """Abstract base class for all states.

    Each state has two constant attributes: :attr:`text` is the short
    text representation which is printed for example at the beginning of
    the summary line. :attr:`code` is the corresponding exit code.
    """

    code: int

    text: str

    def __init__(self, code: int, text: str) -> None:
        self.code = code
        self.text = text

    def __str__(self) -> str:
        """Plugin-API compliant text representation."""
        return self.text

    def __int__(self) -> int:
        """Plugin API compliant exit code."""
        return self.code

    def __gt__(self, other: Any) -> bool:
        return (
            hasattr(other, "code")
            and isinstance(other.code, int)
            and self.code > other.code
        )

    def __eq__(self, other: Any) -> bool:
        return (
            hasattr(other, "code")
            and isinstance(other.code, int)
            and self.code == other.code
            and hasattr(other, "text")
            and isinstance(other.text, str)
            and self.text == other.text
        )

    def __hash__(self) -> int:
        return hash((self.code, self.text))


class Ok(ServiceState):
    def __init__(self) -> None:
        super().__init__(0, "ok")


ok = Ok()


class Warn(ServiceState):
    def __init__(self) -> None:
        super().__init__(1, "warning")


# According to the Nagios development guidelines, this should be Warning,
# not Warn, but renaming the class would occlude the built-in Warning
# exception class.
warn = Warn()


class Critical(ServiceState):
    def __init__(self) -> None:
        super().__init__(2, "critical")


critical = Critical()


class Unknown(ServiceState):
    def __init__(self) -> None:
        super().__init__(3, "unknown")


unknown = Unknown()

# range.py


RangeSpec = Union[str, int, float, "Range"]


class Range:
    """Represents a threshold range.

    The general format is "[@][start:][end]". "start:" may be omitted if
    start==0. "~:" means that start is negative infinity. If `end` is
    omitted, infinity is assumed. To invert the match condition, prefix
    the range expression with "@".

    See
    https://github.com/monitoring-plugins/monitoring-plugin-guidelines/blob/main/definitions/01.range_expressions.md
    for details.
    """

    invert: bool

    start: float

    end: float

    def __init__(self, spec: Optional[RangeSpec] = None) -> None:
        """Creates a Range object according to `spec`.

        :param spec: may be either a string, a float, or another
            Range object.
        """
        spec = spec or ""
        if isinstance(spec, Range):
            self.invert = spec.invert
            self.start = spec.start
            self.end = spec.end
        elif isinstance(spec, int) or isinstance(spec, float):
            self.invert = False
            self.start = 0
            self.end = spec
        else:
            self.start, self.end, self.invert = Range._parse(str(spec))
        Range._verify(self.start, self.end)

    @classmethod
    def _parse(cls, spec: str) -> tuple[float, float, bool]:
        invert = False
        start: float
        start_str: str
        end: float
        end_str: str
        if spec.startswith("@"):
            invert = True
            spec = spec[1:]
        if ":" in spec:
            start_str, end_str = spec.split(":")
        else:
            start_str, end_str = "", spec
        if start_str == "~":
            start = float("-inf")
        else:
            start = cls._parse_atom(start_str, 0)
        end = cls._parse_atom(end_str, float("inf"))
        return start, end, invert

    @staticmethod
    def _parse_atom(atom: str, default: float) -> float:
        if atom == "":
            return default
        if "." in atom:
            return float(atom)
        return int(atom)

    @staticmethod
    def _verify(start: float, end: float) -> None:
        """Throws ValueError if the range is not consistent."""
        if start > end:
            raise ValueError("start %s must not be greater than end %s" % (start, end))

    def match(self, value: float) -> bool:
        """Decides if `value` is inside/outside the threshold.

        :returns: `True` if value is inside the bounds for non-inverted
            Ranges.

        Also available as `in` operator.
        """
        if value < self.start:
            return False ^ self.invert
        if value > self.end:
            return False ^ self.invert
        return True ^ self.invert

    def __contains__(self, value: float) -> bool:
        return self.match(value)

    def _format(self, omit_zero_start: bool = True) -> str:
        result: list[str] = []
        if self.invert:
            result.append("@")
        if self.start == float("-inf"):
            result.append("~:")
        elif not omit_zero_start or self.start != 0:
            result.append(("%s:" % self.start))
        if self.end != float("inf"):
            result.append(("%s" % self.end))
        return "".join(result)

    def __str__(self) -> str:
        """Human-readable range specification."""
        return self._format()

    def __repr__(self) -> str:
        """Parseable range specification."""
        return "Range(%r)" % str(self)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Range):
            return False
        return (
            self.invert == value.invert
            and self.start == self.start
            and self.end == self.end
        )

    @property
    def violation(self) -> str:
        """Human-readable description why a value does not match."""
        return "outside range {0}".format(self._format(False))


# multiarg.py


class MultiArg:
    args: list[str]
    fill: Optional[str]

    def __init__(
        self,
        args: Union[list[str], str],
        fill: Optional[str] = None,
        splitchar: str = ",",
    ) -> None:
        if isinstance(args, list):
            self.args = args
        else:
            self.args = args.split(splitchar)
        self.fill = fill

    def __len__(self) -> int:
        return self.args.__len__()

    def __iter__(self) -> Iterator[str]:
        return self.args.__iter__()

    def __getitem__(self, key: int) -> Optional[str]:
        try:
            return self.args.__getitem__(key)
        except IndexError:
            pass
        if self.fill is not None:
            return self.fill
        try:
            return self.args.__getitem__(-1)
        except IndexError:
            return None


# platform.py


# Changing the badly-named `t` variable at this point is likely API-breaking,
# so it will be left in place.
# pylint: disable-next=invalid-name
def with_timeout(t, func, *args, **kwargs):
    """Call `func` but terminate after `t` seconds."""

    if os.name == "posix":
        signal = importlib.import_module("signal")

        def timeout_handler(signum, frame):
            raise Timeout("{0}s".format(t))

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(t)
        try:
            func(*args, **kwargs)
        finally:
            signal.alarm(0)

    if os.name == "nt":
        # We use a thread here since NT systems don't have POSIX signals.
        threading = importlib.import_module("threading")

        func_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        func_thread.daemon = True  # quit interpreter even if still running
        func_thread.start()
        func_thread.join(t)
        if func_thread.is_alive():
            raise Timeout("{0}s".format(t))


def flock_exclusive(fileobj):
    """Acquire exclusive lock for open file `fileobj`."""

    if os.name == "posix":
        fcntl = importlib.import_module("fcntl")
        fcntl.flock(fileobj, fcntl.LOCK_EX)

    if os.name == "nt":
        msvcrt = importlib.import_module("msvcrt")
        msvcrt.locking(fileobj.fileno(), msvcrt.LK_LOCK, 2147483647)


"""Persistent dict to remember state between invocations.

Cookies are used to remember file positions, counters and the like
between plugin invocations. It is not intended for substantial amounts
of data. Cookies are serialized into JSON and saved to a state file. We
prefer a plain text format to allow administrators to inspect and edit
its content. See :class:`~mplugin.logtail.LogTail` for an
application of cookies to get only new lines of a continuously growing
file.

Cookies are locked exclusively so that at most one process at a time has
access to it. Changes to the dict are not reflected in the file until
:meth:`Cookie.commit` is called. It is recommended to use Cookie as
context manager to get it opened and committed automatically.
"""

# cookie.py


class Cookie(UserDict[str, Any]):
    path: Optional[str]

    def __init__(self, statefile: Optional[str] = None) -> None:
        """Creates a persistent dict to keep state.

        After creation, a cookie behaves like a normal dict.

        :param statefile: file name to save the dict's contents

        .. note:: If `statefile` is empty or None, the Cookie will be
           oblivous, i.e., it will forget its contents on garbage
           collection. This makes it possible to explicitely throw away
           state between plugin runs (for example by a command line
           argument).
        """
        super(Cookie, self).__init__()
        self.path = statefile
        self.fobj = None

    def __enter__(self) -> Self:
        """Allows Cookie to be used as context manager.

        Opens the file and passes a dict-like object into the
        subordinate context. See :meth:`open` for details about opening
        semantics. When the context is left in the regular way (no
        exception raised), the cookie is committed to disk.

        :yields: open cookie
        """
        self.open()
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[type[BaseException]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[TracebackType],
    ) -> None:
        if not exc_type:
            self.commit()
        self.close()

    def open(self):
        """Reads/creates the state file and initializes the dict.

        If the state file does not exist, it is touched into existence.
        An exclusive lock is acquired to ensure serialized access. If
        :meth:`open` fails to parse file contents, it truncates
        the file before raising an exception. This guarantees that
        plugins will not fail repeatedly when their state files get
        damaged.

        :returns: Cookie object (self)
        :raises ValueError: if the state file is corrupted or does not
            deserialize into a dict
        """
        self.fobj = self._create_fobj()
        flock_exclusive(self.fobj)
        if os.fstat(self.fobj.fileno()).st_size:
            try:
                self.data = self._load()
            except ValueError:
                self.fobj.truncate(0)
                raise
        return self

    def _create_fobj(self):
        if not self.path:
            return TemporaryFile(
                "w+", encoding="ascii", prefix="oblivious_cookie_", dir=None
            )
        # mode='a+' has problems with mixed R/W operation on Mac OS X
        try:
            return open(self.path, "r+", encoding="ascii")
        except IOError:
            return open(self.path, "w+", encoding="ascii")

    def _load(self) -> dict[str, Any]:
        if not self.fobj:
            raise RuntimeError("file object is none")
        self.fobj.seek(0)
        data = json.load(self.fobj)
        if not isinstance(data, dict):
            raise ValueError(
                "format error: cookie does not contain dict", self.path, data
            )
        return typing.cast(dict[str, Any], data)

    def close(self) -> None:
        """Closes a cookie and its underlying state file.

        This method has no effect if the cookie is already closed.
        Once the cookie is closed, any operation (like :meth:`commit`)
        will raise an exception.
        """
        if not self.fobj:
            return
        self.fobj.close()
        self.fobj = None

    def commit(self) -> None:
        """Persists the cookie's dict items in the state file.

        The cookies content is serialized as JSON string and saved to
        the state file. The buffers are flushed to ensure that the new
        content is saved in a durable way.
        """
        if not self.fobj:
            raise IOError("cannot commit closed cookie", self.path)
        self.fobj.seek(0)
        self.fobj.truncate()
        json.dump(self.data, self.fobj)
        self.fobj.write("\n")
        self.fobj.flush()
        os.fsync(self.fobj)

# logtail.py

class LogTail:
    """Access previously unseen parts of a growing file.

    LogTail builds on :class:`~.cookie.Cookie` to access new lines of a
    continuosly growing log file. It should be used as context manager that
    provides an iterator over new lines to the subordinate context. LogTail
    saves the last file position into the provided cookie object.
    As the path to the log file is saved in the cookie, several LogTail
    instances may share the same cookie.
    """

    path: str
    cookie: "Cookie"
    logfile: typing.Optional[BufferedIOBase] = None
    stat: typing.Optional[os.stat_result]

    def __init__(self, path: str, cookie: "Cookie") -> None:
        """Creates new LogTail context.

        :param path: path to the log file that is to be observed
        :param cookie: :class:`~.cookie.Cookie` object to save the last
            file position
        """
        self.path = os.path.abspath(path)
        self.cookie = cookie
        self.logfile = None
        self.stat = None

    def _seek_if_applicable(self, fileinfo: dict[str, typing.Any]) -> None:
        self.stat = os.stat(self.path)
        if (
            self.stat.st_ino == fileinfo.get("inode", -1)
            and self.stat.st_size >= fileinfo.get("pos", 0)
            and self.logfile is not None
        ):
            self.logfile.seek(fileinfo["pos"])

    def __enter__(self) -> typing.Generator[bytes, typing.Any, None]:
        """Seeks to the last seen position and reads new lines.

        The last file position is read from the cookie. If the log file
        has not been changed since the last invocation, LogTail seeks to
        that position and reads new lines. Otherwise, the position saved
        in the cookie is reset and LogTail reads from the beginning.
        After leaving the subordinate context, the new position is saved
        in the cookie and the cookie is closed.

        :yields: new lines as bytes strings
        """
        self.logfile = open(self.path, "rb")
        self.cookie.open()
        self._seek_if_applicable(self.cookie.get(self.path, {}))
        line = self.logfile.readline()
        while len(line):
            yield line
            line = self.logfile.readline()

    def __exit__(
        self,
        exc_type: typing.Optional[type[BaseException]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[TracebackType],
    ) -> None:
        if not exc_type and self.stat is not None and self.logfile is not None:
            self.cookie[self.path] = dict(
                inode=self.stat.st_ino, pos=self.logfile.tell()
            )
            self.cookie.commit()
        self.cookie.close()
        if self.logfile is not None:
            self.logfile.close()
