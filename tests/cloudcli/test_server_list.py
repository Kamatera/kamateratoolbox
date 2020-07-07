def test_server_list(cloudcli, session_server_powered_on, session_server_powered_off):
    res = cloudcli("server", "list")
    assert session_server_powered_off["name"] in res
    assert session_server_powered_on["name"] in res
    res = cloudcli("server", "list", "--format", "json")
    servers = {server["name"]: server for server in res}
    assert session_server_powered_on["name"] in servers
    assert session_server_powered_off["name"] in servers
    res = cloudcli("server", "list", "--format", "yaml")
    servers = {server["name"]: server for server in res}
    assert session_server_powered_on["name"] in servers
    assert session_server_powered_off["name"] in servers
