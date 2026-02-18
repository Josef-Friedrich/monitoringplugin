import mplugin
from mplugin.summary import Summary


class TestSummary:
    def test_ok_returns_first_result(self):
        results = mplugin.Results(
            mplugin.Result(mplugin.ok, "result 1"),
            mplugin.Result(mplugin.ok, "result 2"),
        )
        assert "result 1" == Summary().ok(results)

    def test_problem_returns_first_significant(self):
        results = mplugin.Results(
            mplugin.Result(mplugin.ok, "result 1"),
            mplugin.Result(mplugin.critical, "result 2"),
        )
        assert "result 2" == Summary().problem(results)

    def test_verbose(self):
        assert ["critical: reason1", "warning: reason2"] == Summary().verbose(
            mplugin.Results(
                mplugin.Result(mplugin.critical, "reason1"),
                mplugin.Result(mplugin.ok, "ignore"),
                mplugin.Result(mplugin.warn, "reason2"),
            )
        )
