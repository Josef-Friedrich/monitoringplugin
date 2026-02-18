"""Platform-specific services."""

import os

platform = __import__(
    "mplugin.platform.{0}".format(os.name),
    fromlist=["with_timeout", "flock_exclusive"],
)

with_timeout = platform.with_timeout
flock_exclusive = platform.flock_exclusive
