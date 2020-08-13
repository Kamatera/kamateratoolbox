import pytest
import datetime
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers


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


def test_server_statistics_all(session_server_powered_on):
    res = cloudcli_server_request("/server/statistics", method="POST", json={
        "name": session_server_powered_on["name"],
        "all": True,
        "period": "1h"
    })
    _assert_stats(res)
    res = cloudcli_server_request("/server/statistics", method="POST", json={
        "name": session_server_powered_on["name"],
        "all": True,
        "startdate": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y%m%d"),
        "enddate": datetime.datetime.now().strftime("%Y%m%d")
    })
    _assert_stats(res)


def test_server_statistics(session_server_powered_on):
    for stat in ["cpu", "ram", "network", "disksIops", "disksTransfer"]:
        print("Testing stat %s" % stat)
        res = cloudcli_server_request("/server/statistics", method="POST", json={
            "name": session_server_powered_on["name"],
            stat: True,
            "period": "1h"
        })
        _assert_stats(res)
        res = cloudcli_server_request("/server/statistics", method="POST", json={
            "name": session_server_powered_on["name"],
            stat: True,
            "startdate": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y%m%d"),
            "enddate": datetime.datetime.now().strftime("%Y%m%d")
        })
        _assert_stats(res)
