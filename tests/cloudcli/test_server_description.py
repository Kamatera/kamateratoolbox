import secrets
from ..common import assert_only_one_server_cloudcli, assert_no_matching_servers_cloudcli, get_server_id


def test_server_description_only_one_server(cloudcli, session_server_powered_on, session_server_powered_off):
    assert_only_one_server_cloudcli([session_server_powered_on, session_server_powered_off], cloudcli, ["server", "description"])


def test_server_description_no_matching_servers(cloudcli):
    assert_no_matching_servers_cloudcli(cloudcli, ["server", "description"])


def test_server_description_get(cloudcli, session_server_powered_on):
    res = cloudcli("server", "description", "--name", session_server_powered_on["name"], "--format", "json")
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == session_server_powered_on["name"]
    assert server["description"] == "Ubuntu Server version 18.04 LTS (bionic) 64-bit"


def test_server_description_get_by_id(cloudcli, session_server_powered_on):
    res = cloudcli("server", "description", "--id", get_server_id(session_server_powered_on), "--format", "json")
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == session_server_powered_on["name"]
    assert server["description"] == "Ubuntu Server version 18.04 LTS (bionic) 64-bit"


def test_server_description_set(cloudcli, temp_server):
    new_description = "My Server Descriiption!!!\n%s" % secrets.token_urlsafe(20)
    res = cloudcli("server", "description", "--name", temp_server["name"], "--set", new_description, "--format", "json")
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == new_description
    res = cloudcli("server", "description", "--name", temp_server["name"], "--format", "json")
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == new_description


def test_server_description_set_by_id(cloudcli, temp_server):
    new_description = "My Server Descriiption!!!\n%s" % secrets.token_urlsafe(20)
    res = cloudcli("server", "description", "--id", get_server_id(temp_server), "--set", new_description, "--format", "json")
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == new_description
    res = cloudcli("server", "description", "--id", get_server_id(temp_server), "--format", "json")
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == new_description
