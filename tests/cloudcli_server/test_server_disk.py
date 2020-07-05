import pytest
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, wait_command


def test_server_disk_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server("/server/disk")


def test_server_disk_no_matching_servers():
    assert_no_matching_servers("/server/disk")


def test_server_disk_list(session_server_powered_on):
    res = cloudcli_server_request("/server/disk", method="POST", json={
        "name": session_server_powered_on["name"]
    })
    assert len(res) == 1
    disk = res[0]
    assert set(disk.keys()) == {"id", "size"}
    assert disk["id"] == 0
    assert disk["size"] == "10gb"


def test_server_disk_operations(temp_server):
    print("Add disk")
    res = cloudcli_server_request("/server/disk", method="POST", json={
        "name": temp_server["name"],
        "add": "20gb"
    })
    command_id = int(res)
    wait_command(command_id)
    res = cloudcli_server_request("/server/disk", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 2
    assert res[1]["id"] == 1
    assert res[1]["size"] == "20gb"
    print("Resize disk")
    res = cloudcli_server_request("/server/disk", method="POST", json={
        "name": temp_server["name"],
        "resize": "1",
        "size": "30gb"
    })
    command_id = int(res)
    wait_command(command_id)
    res = cloudcli_server_request("/server/disk", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 2
    assert res[1]["size"] == "30gb"
    print("Try to remove disk, but server has snapshot from resize operation")
    with pytest.raises(Exception, match="server has snapshots"):
        cloudcli_server_request("/server/disk", method="POST", json={
            "name": temp_server["name"],
            "remove": "1"
        })
    print("Remove snapshot")
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    snapshot_id = res[0]["id"]
    res = cloudcli_server_request("/server/snapshot", method="POST", json={
        "name": temp_server["name"],
        "delete": str(snapshot_id)
    })
    command_id = int(res)
    wait_command(command_id)
    print("Remove disk, no snapshots now")
    res = cloudcli_server_request("/server/disk", method="POST", json={
        "name": temp_server["name"],
        "remove": "1"
    })
    command_id = int(res)
    wait_command(command_id)
    res = cloudcli_server_request("/server/disk", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
