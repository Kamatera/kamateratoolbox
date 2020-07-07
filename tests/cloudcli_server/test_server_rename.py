from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, get_server_name, wait_command, get_server_id


def test_server_rename_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/service/server/rename", {"new-name": "foobar"})


def test_server_rename_no_matching_servers():
    assert_no_matching_servers("/service/server/rename", {"new-name": "foobar"})


def test_server_rename(temp_server):
    old_name = temp_server["name"]
    new_name = get_server_name()
    res = cloudcli_server_request("/service/server/rename", method="POST", json={
        "name": old_name,
        "new-name": new_name
    })
    assert len(res) == 1
    wait_command(res[0])
    temp_server["name"] = new_name
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": new_name
    })
    assert len(res) == 1
    assert res[0]["name"] == new_name


def test_server_rename_by_id(temp_server):
    new_name = get_server_name()
    res = cloudcli_server_request("/service/server/rename", method="POST", json={
        "id": get_server_id(temp_server),
        "new-name": new_name
    })
    assert len(res) == 1
    wait_command(res[0])
    temp_server["name"] = new_name
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "id": get_server_id(temp_server)
    })
    assert len(res) == 1
    assert res[0]["name"] == new_name
