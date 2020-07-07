from ..common import cloudcli_server_request, get_server_id


def test_server_list(session_server_powered_on, session_server_powered_off):
    res = cloudcli_server_request("/service/servers")
    test_server = None
    has_other_server = False
    for server in res:
        if server["name"] == session_server_powered_on["name"]:
            test_server = server
        elif server["name"] == session_server_powered_off["name"]:
            has_other_server = True
    assert has_other_server
    assert test_server
    assert set(test_server.keys()) == {"id", "datacenter", "name", "power"}
    assert test_server["power"] == "on"
    assert len(test_server["id"]) > 10
    assert test_server["id"] == get_server_id(session_server_powered_on)
    assert test_server["datacenter"] == session_server_powered_on["create_request_data"]["datacenter"]
