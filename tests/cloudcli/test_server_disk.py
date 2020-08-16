import pytest
from ..common import assert_only_one_server_cloudcli, assert_no_matching_servers_cloudcli, get_server_id
from ..conftest import CloudcliFailedException


def test_server_disk_only_one_server(cloudcli, session_server_powered_on, session_server_powered_off):
    assert_only_one_server_cloudcli([session_server_powered_on, session_server_powered_off], cloudcli, ["server", "disk"])


def test_server_disk_no_matching_servers(cloudcli):
    assert_no_matching_servers_cloudcli(cloudcli, ["server", "disk"])


def test_server_disk_list(cloudcli, session_server_powered_on):
    res = cloudcli("server", "disk", "--name", session_server_powered_on["name"], "--format", "json")
    assert len(res) == 1
    disk = res[0]
    assert set(disk.keys()) == {"id", "size"}
    assert disk["id"] == 0
    assert disk["size"] == "10gb"


def test_server_disk_list_by_id(cloudcli, session_server_powered_on):
    res = cloudcli("server", "disk", "--id", get_server_id(session_server_powered_on), "--format", "json")
    assert len(res) == 1
    disk = res[0]
    assert set(disk.keys()) == {"id", "size"}
    assert disk["id"] == 0
    assert disk["size"] == "10gb"


def test_server_disk_operations(cloudcli, temp_server):
    print("Add disk")
    cloudcli("server", "disk", "--name", temp_server["name"], "--add", "20gb", "--wait")
    res = cloudcli("server", "disk", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 2
    assert res[1]["id"] == 1
    assert res[1]["size"] == "20gb"
    print("Resize disk")
    cloudcli("server", "disk", "--name", temp_server["name"], "--resize", "1", "--size", "30gb", "--wait")
    res = cloudcli("server", "disk", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 2
    assert res[1]["size"] == "30gb"
    print("Try to remove disk, but server has snapshot from resize operation")
    with pytest.raises(Exception, match="server has snapshots"):
        cloudcli("server", "disk", "--name", temp_server["name"], "--remove", "1", "--wait", ignore_wait_error=False)
    print("Remove snapshot")
    res = cloudcli("server", "snapshot", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
    snapshot_id = res[0]["id"]
    cloudcli("server", "snapshot", "--name", temp_server["name"], "--delete", str(snapshot_id), "--wait")
    print("Remove disk, no snapshots now")
    cloudcli("server", "disk", "--name", temp_server["name"], "--remove", "1", "--wait")
    res = cloudcli("server", "disk", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
