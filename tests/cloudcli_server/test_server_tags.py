from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, get_server_id


def test_server_tags_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/tags")


def test_server_tags_no_matching_servers():
    assert_no_matching_servers("/server/tags")


def test_server_tags(temp_server):
    server_id = get_server_id(temp_server)
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 0
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"],
        "add": "foo"
    })
    assert len(res) == 1
    assert set(res[0].keys()) == {"server id", "tag name"}
    assert res[0]["server id"] == server_id
    assert res[0]["tag name"] == "foo"
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"],
        "add": "bar"
    })
    assert len(res) == 2
    assert set(res[0].keys()) == {"server id", "tag name"}
    assert res[0]["server id"] == server_id
    assert res[1]["server id"] == server_id
    assert set([r["tag name"] for r in res]) == {"foo", "bar"}
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"],
        "remove": "foo"
    })
    assert len(res) == 1
    assert set(res[0].keys()) == {"server id", "tag name"}
    assert res[0]["server id"] == server_id
    assert res[0]["tag name"] == "bar"
