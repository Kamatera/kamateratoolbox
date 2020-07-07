import secrets
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, get_server_id


def test_server_description_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/description")


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


def test_server_description_get_by_id(session_server_powered_on):
    res = cloudcli_server_request("/server/description", method="POST", json={
        "id": get_server_id(session_server_powered_on)
    })
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == session_server_powered_on["name"]
    assert server["description"] == "Ubuntu Server version 18.04 LTS (bionic) 64-bit"


def test_server_description_set(temp_server):
    new_description = "My Server Descriiption!!!\n%s" % secrets.token_urlsafe(20)
    res = cloudcli_server_request("/server/description", method="POST", json={
        "name": temp_server["name"],
        "set": new_description
    })
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == new_description
    res = cloudcli_server_request("/server/description", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == new_description


def test_server_description_set_by_id(temp_server):
    new_description = "My Server Descriiption!!!\n%s" % secrets.token_urlsafe(20)
    res = cloudcli_server_request("/server/description", method="POST", json={
        "id": get_server_id(temp_server),
        "set": new_description
    })
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == new_description
    res = cloudcli_server_request("/server/description", method="POST", json={
        "id": get_server_id(temp_server)
    })
    assert len(res) == 1
    server = res[0]
    assert set(server.keys()) == {"description", "name"}
    assert server["name"] == temp_server["name"]
    assert server["description"] == new_description
