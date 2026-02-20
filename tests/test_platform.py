import time

import pytest

import mplugin
from mplugin import with_timeout


class TestPlatform:
    def test_timeout(self):
        with pytest.raises(mplugin.Timeout):
            with_timeout(1, time.sleep, 2)
