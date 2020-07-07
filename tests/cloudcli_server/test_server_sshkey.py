import datetime
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, get_server_id


def test_server_sshkey_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/service/server/sshkey")


def test_server_sshkey_no_matching_servers():
    assert_no_matching_servers("/service/server/sshkey")


def test_server_sshkey(session_server_powered_on):
    server_id = get_server_id(session_server_powered_on)
    res = cloudcli_server_request("/service/server/sshkey", method="POST", json={
        "id": server_id
    })
    assert len(res) == 1
    assert set(res[0].keys()) == {"id", "name", "externalIp"}
    assert res[0]["id"] == server_id
    assert res[0]["name"] == session_server_powered_on["name"]
    assert len(res[0]["externalIp"]) > 5
