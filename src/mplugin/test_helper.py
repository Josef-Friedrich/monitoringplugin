from __future__ import annotations

import io
import typing
from unittest.mock import Mock

from mplugin import ServiceState, state


class MockResult:
    """A class to collect all results of a mocked execution of the main
    function."""

    __sys_exit: Mock
    __stdout: typing.Optional[str]
    __stderr: typing.Optional[str]

    def __init__(
        self,
        sys_exit_mock: Mock,
        stdout: typing.Optional[io.StringIO],
        stderr: typing.Optional[io.StringIO],
    ) -> None:
        self.__sys_exit = sys_exit_mock

        if stdout is not None:
            out = stdout.getvalue()
            if out != "":
                self.__stdout = out

        if stderr is not None:
            err = stderr.getvalue()
            if err != "":
                self.__stdout = err

    @property
    def exitcode(self) -> int:
        """The captured exit code"""
        return int(self.__sys_exit.call_args[0][0])

    @property
    def state(self) -> ServiceState:
        return state(self.exitcode)

    @property
    def stdout(self) -> typing.Optional[str]:
        """The function ``redirect_stdout()`` is used to capture the ``stdout``
        output."""
        if self.__stdout:
            return self.__stdout
        return None

    @property
    def stderr(self) -> typing.Optional[str]:
        """The function ``redirect_stderr()`` is used to capture the ``stderr``
        output."""
        if self.__stderr:
            return self.__stderr
        return None

    @property
    def output(self) -> str:
        """A combined string of the captured stderr, stdout  and the print
        calls. Somehow the whole stdout couldn’t be read. The help text could
        be read, but not the plugin output using the function
        ``redirect_stdout()``."""
        out: str = ""

        if self.__stderr:
            out += self.__stderr

        if self.__stdout:
            out += self.__stdout

        return out

    @property
    def first_line(self) -> typing.Optional[str]:
        """The first line of the output without a newline break at the
        end as a string.
        """
        if self.output:
            return self.output.split("\n", 1)[0]
        return None
