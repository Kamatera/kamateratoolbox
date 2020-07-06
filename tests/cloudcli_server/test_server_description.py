from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers


def test_server_description_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server("/server/description")


def test_server_description_no_matching_servers():
    assert_no_matching_servers("/server/description")


def test_server_description_get(session_server_powered_on):
    res = cloudcli_server_request("/server/description", method="POST", json={
        "name": session_server_powered_on["name"]
    })
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == session_server_powered_on["name"]
    assert server["description"] == "Ubuntu Server version 18.04 LTS (bionic) 64-bit"


def test_server_description_set(temp_server):
    res = cloudcli_server_request("/server/description", method="POST", json={
        "name": temp_server["name"],
        "set": "My Server Descriiption!!!"
    })
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == "My Server Descriiption!!!"
    res = cloudcli_server_request("/server/description", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == "My Server Descriiption!!!"