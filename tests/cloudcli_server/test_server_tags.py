from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, get_server_id


def test_server_tags_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/tags")


def test_server_tags_no_matching_servers():
    assert_no_matching_servers("/server/tags")


def test_server_tags(temp_server):
    server_id = get_server_id(temp_server)

    # new server: no tags
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"]
    })
    assert res == []

    # add tag "foo"
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"],
        "add": "foo"
    })
    assert res == [
        {'server id': server_id, 'tag name': 'foo'}
    ]

    # add tag "bar"
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"],
        "add": "bar"
    })
    assert len(res) == 2
    assert set([r['tag name'] for r in res]) == {"foo", "bar"}

    # remove tag "foo"
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"],
        "remove": "foo"
    })
    assert res == [
        {'server id': server_id, 'tag name': 'bar'}
    ]

    # list tags
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"]
    })
    assert res == [
        {'server id': server_id, 'tag name': 'bar'}
    ]

    # remove tag bar
    res = cloudcli_server_request("/server/tags", method="POST", json={
        "name": temp_server["name"],
        "remove": "bar"
    })
    assert res == []
