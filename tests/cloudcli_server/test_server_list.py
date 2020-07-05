from ..common import cloudcli_server_request


def test_server_list(session_server_powered_on):
    res = cloudcli_server_request("/service/servers")
    test_server = None
    for server in res:
        if server["name"] == session_server_powered_on["name"]:
            test_server = server
            break
    assert test_server
    assert set(test_server.keys()) == {"id", "datacenter", "name", "power"}
    assert test_server["power"] == "on"
    assert len(test_server["id"]) > 10
    assert test_server["datacenter"] == session_server_powered_on["create_request_data"]["datacenter"]
