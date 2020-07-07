import datetime
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, wait_command


def test_server_snapshot_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/snapshot")


def test_server_snapshot_no_matching_servers():
    assert_no_matching_servers("/server/snapshot")


def test_server_snapshot(temp_server):
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 0
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"],
        "create": "snap1"
    })
    wait_command(res)
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert set(res[0].keys()) == {"id", "name", "date", "active", "depth", "child"}
    assert res[0]["name"].startswith("snap1-")
    assert datetime.datetime.strptime(res[0]["date"], "%d/%m/%Y %H:%M:%S").date() == datetime.datetime.now().date()
    assert res[0]["active"] == True
    assert res[0]["depth"] == 0
    assert res[0]["child"] == []
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"],
        "create": "snap2"
    })
    wait_command(res)
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 2
    snaps = {snap["name"].split("-")[0]: snap for snap in res}
    assert snaps["snap2"]["active"] == True
    assert snaps["snap2"]["depth"] == 1
    assert snaps["snap1"]["active"] == False
    assert snaps["snap1"]["depth"] == 0
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"],
        "revert": str(snaps["snap1"]["id"])
    })
    wait_command(res)
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 2
    snaps = {snap["name"].split("-")[0]: snap for snap in res}
    assert snaps["snap2"]["active"] == False
    assert snaps["snap1"]["active"] == True
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"],
        "delete": str(snaps["snap1"]["id"])
    })
    wait_command(res)
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    snaps = {snap["name"].split("-")[0]: snap for snap in res}
    assert snaps["snap2"]["active"] == False
