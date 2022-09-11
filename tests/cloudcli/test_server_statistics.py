import datetime
from ..cloudcli_server.test_server_statistics import assert_all_stats, STAT_CATEGORIES, assert_stats_category


def test_server_statistics_all(cloudcli, session_server_powered_on):
    res = cloudcli(
        "server", "statistics", "--name", session_server_powered_on["name"],
        "--all", "--period", "1h", "--format", "json"
    )
    assert_all_stats(res)
    res = cloudcli(
        "server", "statistics", "--name", session_server_powered_on["name"], "--all",
        "--startdate", (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y%m%d"),
        "--enddate", datetime.datetime.now().strftime("%Y%m%d"),
        "--format", "json"
    )
    assert_all_stats(res)


def test_server_statistics_categories(cloudcli, session_server_powered_on):
    for category in STAT_CATEGORIES.keys():
        print("Testing category %s" % category)
        res = cloudcli(
            "server", "statistics", "--name", session_server_powered_on["name"],
            f"--{category}", "--period", "1h", "--format", "json"
        )
        assert_stats_category(category, res)
        res = cloudcli(
            "server", "statistics", "--name", session_server_powered_on["name"], f"--{category}",
            "--startdate", (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y%m%d"),
            "--enddate", datetime.datetime.now().strftime("%Y%m%d"),
            "--format", "json"
        )
        assert_stats_category(category, res)
