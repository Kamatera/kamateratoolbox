from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, assert_server_ssh


def test_server_attach_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/service/server/ssh")


def test_server_attach_no_matching_servers():
    assert_no_matching_servers("/service/server/ssh")


def test_server_attach(session_server_powered_on):
    server_id, server_external_ip = assert_server_ssh(session_server_powered_on)
    print("Getting attach details by id")
    res = cloudcli_server_request("/service/server/ssh", method="POST", json={
        "id": server_id
    })
    assert len(res) == 1
    assert set(res[0].keys()) == {"id", "name", "externalIp"}
    assert res[0]["id"] == server_id
    assert res[0]["name"] == session_server_powered_on["name"]
    assert res[0]["externalIp"] == server_external_ip
