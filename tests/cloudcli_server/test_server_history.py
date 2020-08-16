import datetime
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, wait_command, get_server_id


def test_server_history_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/history")


def test_server_history_no_matching_servers():
    assert_no_matching_servers("/server/history")


def test_server_history(temp_server):
    print("Reboot server to have some history")
    res = cloudcli_server_request("/service/server/reboot", method="POST", json={
        "name": temp_server["name"],
    })
    command_id = int(res[0])
    wait_command(command_id)
    res = cloudcli_server_request("/server/history", method="POST", json={
        "name": temp_server["name"],
    })
    assert len(res) == 2
    assert set(res[0].keys()) == {"date", "user", "action"}
    assert datetime.datetime.strptime(res[0]["date"], "%d/%m/%Y %H:%M:%S").date() == datetime.datetime.now().date()
    assert len(res[0]["user"]) > 3
    assert len(res[0]["action"]) > 3
    print("Get history by id")
    res = cloudcli_server_request("/server/history", method="POST", json={
        "id": get_server_id(temp_server),
    })
    assert len(res) == 2
    assert set(res[0].keys()) == {"date", "user", "action"}
    assert datetime.datetime.strptime(res[0]["date"], "%d/%m/%Y %H:%M:%S").date() == datetime.datetime.now().date()
    assert len(res[0]["user"]) > 3
    assert len(res[0]["action"]) > 3
