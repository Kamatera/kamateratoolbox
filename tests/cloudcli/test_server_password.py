from ..common import assert_no_matching_servers_cloudcli, get_server_password, assert_server_ssh


def test_server_password_no_matching_servers(cloudcli):
    assert_no_matching_servers_cloudcli(cloudcli, ["server", "passwordreset", "--password", "Aa123456789!!!!"])


def test_server_password(cloudcli, temp_server):
    print("Setting password by server name")
    temp_server["password"] = get_server_password()
    cloudcli("server", "passwordreset", "--name", temp_server["name"], "--password", temp_server["password"], "--wait")
    server_id, server_external_ip = assert_server_ssh(temp_server)
    print("Setting password by server id")
    temp_server["password"] = get_server_password()
    cloudcli("server", "passwordreset", "--id", server_id, "--password", temp_server["password"], "--wait")
    assert_server_ssh(temp_server)


def test_multiple_server_passwords(cloudcli, temp_servers_factory):
    server1 = temp_servers_factory("create")
    server2 = temp_servers_factory("create")
    temp_servers_factory("wait")
    print("Setting passwords by server names")
    server1["password"] = server2["password"] = get_server_password()
    cloudcli("server", "passwordreset", "--name", "%s|%s" % (server1["name"], server2["name"]), "--password", server1["password"], "--wait")
    assert_server_ssh(server1)
    assert_server_ssh(server2)
