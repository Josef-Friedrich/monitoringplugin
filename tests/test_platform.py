# -*- coding: utf-8 -*-
import time

import monitoringplugin
import pytest
from monitoringplugin.platform import with_timeout

try:
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest


class TestPlatform:
    def test_timeout(self):
        with pytest.raises(monitoringplugin.Timeout):
            with_timeout(1, time.sleep, 2)
