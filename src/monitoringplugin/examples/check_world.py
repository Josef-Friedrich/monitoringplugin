#!python

"""Hello world Nagios check."""

import monitoringplugin


class World(monitoringplugin.Resource):
    def probe(self):
        return [monitoringplugin.Metric("world", True, context="null")]


def main():
    check = monitoringplugin.Check(World())
    check.main()


if __name__ == "__main__":
    main()
