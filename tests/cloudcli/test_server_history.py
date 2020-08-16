import datetime
from ..common import assert_only_one_server_cloudcli, assert_no_matching_servers_cloudcli, get_server_id


def test_server_history_only_one_server(cloudcli, session_server_powered_on, session_server_powered_off):
    assert_only_one_server_cloudcli([session_server_powered_on, session_server_powered_off], cloudcli, ["server", "history"])


def test_server_history_no_matching_servers(cloudcli):
    assert_no_matching_servers_cloudcli(cloudcli, ["server", "history"])


def test_server_history(cloudcli, temp_server):
    print("Reboot server to have some history")
    cloudcli("server", "reboot", "--name", temp_server["name"], "--wait")
    res = cloudcli("server", "history", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 2
    assert set(res[0].keys()) == {"date", "user", "action"}
    assert datetime.datetime.strptime(res[0]["date"], "%d/%m/%Y %H:%M:%S").date() == datetime.datetime.now().date()
    assert len(res[0]["user"]) > 3
    assert len(res[0]["action"]) > 3
    print("Get history by id")
    res = cloudcli("server", "history", "--id", get_server_id(temp_server), "--format", "json")
    assert len(res) == 2
    assert set(res[0].keys()) == {"date", "user", "action"}
    assert datetime.datetime.strptime(res[0]["date"], "%d/%m/%Y %H:%M:%S").date() == datetime.datetime.now().date()
    assert len(res[0]["user"]) > 3
    assert len(res[0]["action"]) > 3
