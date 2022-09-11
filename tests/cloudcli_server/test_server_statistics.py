import datetime

import pytest

from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers
from ..kamatera_api.test_statistics import assert_stat_series_data, STAT_CATEGORIES


def test_server_statistics_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/statistics")


def test_server_statistics_no_matching_servers():
    assert_no_matching_servers("/server/statistics")


def test_server_statistics_errors(session_server_powered_on):
    with pytest.raises(Exception, match="choose a metric to show"):
        cloudcli_server_request("/server/statistics", method="POST", json={
            "name": session_server_powered_on["name"],
        })
    with pytest.raises(Exception, match="specify period, or startdate and enddate flags"):
        cloudcli_server_request("/server/statistics", method="POST", json={
            "name": session_server_powered_on["name"],
            "all": True,
        })
    with pytest.raises(Exception, match="specify period, or startdate and enddate flags"):
        cloudcli_server_request("/server/statistics", method="POST", json={
            "name": session_server_powered_on["name"],
            "all": True,
            "startdate": "foobar"
        })
    with pytest.raises(Exception, match="specify period, or startdate and enddate flags"):
        cloudcli_server_request("/server/statistics", method="POST", json={
            "name": session_server_powered_on["name"],
            "all": True,
            "enddate": "foobar"
        })


def _assert_stats(res):
    all_stats = {}
    for stats in res:
        for stat in stats:
            assert set(stat.keys()) == {"series", "data"}
            assert stat["series"] not in all_stats
            all_stats[stat["series"]] = stat["data"]
    return all_stats


def assert_all_stats(res):
    stats = _assert_stats(res)
    all_series_names = set()
    for values in STAT_CATEGORIES.values():
        all_series_names.update(values)
    assert set(stats.keys()) == all_series_names
    for name, data in stats.items():
        assert_stat_series_data(name, data)


def assert_stats_category(category, res):
    stats = _assert_stats(res)
    assert set(stats.keys()) == STAT_CATEGORIES[category]
    for name, data in stats.items():
        assert_stat_series_data(name, data)


def test_server_statistics_all(session_server_powered_on):
    res = cloudcli_server_request("/server/statistics", method="POST", json={
        "name": session_server_powered_on["name"],
        "all": True,
        "period": "1h"
    })
    assert_all_stats(res)
    res = cloudcli_server_request("/server/statistics", method="POST", json={
        "name": session_server_powered_on["name"],
        "all": True,
        "startdate": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y%m%d"),
        "enddate": datetime.datetime.now().strftime("%Y%m%d")
    })
    assert_all_stats(res)


def test_server_statistics(session_server_powered_on):
    for category in STAT_CATEGORIES.keys():
        print("Testing category %s" % category)
        res = cloudcli_server_request("/server/statistics", method="POST", json={
            "name": session_server_powered_on["name"],
            category: True,
            "period": "1h"
        })
        assert_stats_category(category, res)
        res = cloudcli_server_request("/server/statistics", method="POST", json={
            "name": session_server_powered_on["name"],
            category: True,
            "startdate": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y%m%d"),
            "enddate": datetime.datetime.now().strftime("%Y%m%d")
        })
        assert_stats_category(category, res)
