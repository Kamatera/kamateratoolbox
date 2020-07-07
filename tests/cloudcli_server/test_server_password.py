from ..common import cloudcli_server_request, assert_no_matching_servers, get_server_id, get_server_password, wait_command, assert_server_ssh


def test_server_password_no_matching_servers():
    assert_no_matching_servers("/service/server/password", {"password": "Aa123456789!!!!"})


def test_server_password(temp_server):
    print("Setting password by server name")
    temp_server["password"] = get_server_password()
    res = cloudcli_server_request("/service/server/password", method="POST", json={
        "name": temp_server["name"],
        "password": temp_server["password"]
    })
    assert len(res) == 1
    command_id = int(res[0])
    wait_command(command_id)
    server_id, server_external_ip = assert_server_ssh(temp_server)
    print("Setting password by server id")
    temp_server["password"] = get_server_password()
    res = cloudcli_server_request("/service/server/password", method="POST", json={
        "id": server_id,
        "password": temp_server["password"]
    })
    assert len(res) == 1
    command_id = int(res[0])
    wait_command(command_id)
    assert_server_ssh(temp_server)


def test_multiple_server_passwords(temp_servers_factory):
    server1 = temp_servers_factory("create")
    server2 = temp_servers_factory("create")
    temp_servers_factory("wait")
    print("Setting passwords by server names")
    server1["password"] = server2["password"] = get_server_password()
    res = cloudcli_server_request("/service/server/password", method="POST", json={
        "name": "%s|%s" % (server1["name"], server2["name"]),
        "password": server1["password"]
    })
    assert len(res) == 2
    for command_id in res:
        wait_command(int(command_id))
    assert_server_ssh(server1)
    assert_server_ssh(server2)
