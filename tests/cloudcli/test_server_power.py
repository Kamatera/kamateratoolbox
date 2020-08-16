from ..common import assert_no_matching_servers_cloudcli


def test_server_power_on_no_matching_servers(cloudcli):
    assert_no_matching_servers_cloudcli(cloudcli, ["server", "poweron"])


def test_server_power_off_no_matching_servers(cloudcli):
    assert_no_matching_servers_cloudcli(cloudcli, ["server", "poweroff"])


def test_server_power_reboot_no_matching_servers(cloudcli):
    assert_no_matching_servers_cloudcli(cloudcli, ["server", "reboot"])


def test_server_power(cloudcli, temp_server):
    print("poweroff server")
    cloudcli("server", "poweroff", "--name", temp_server["name"], "--wait")
    res = cloudcli("server", "info", "--name", temp_server["name"], parse=True)
    assert len(res) == 1
    server_id = res[0]["id"]
    assert res[0]["power"] == "off"
    cloudcli("server", "poweron", "--id", server_id, "--wait")
    res = cloudcli("server", "info", "--id", server_id, parse=True)
    assert len(res) == 1
    assert res[0]["power"] == "on"
    cloudcli("server", "reboot", "--id", server_id, "--wait")
    res = cloudcli("server", "info", "--id", server_id, parse=True)
    assert len(res) == 1
    assert res[0]["power"] == "on"


def test_multiple_servers_power(cloudcli, temp_servers_factory):
    server1 = temp_servers_factory("create")
    server2 = temp_servers_factory("create")
    temp_servers_factory("wait")
    print("Powering off servers")
    cloudcli("server", "poweroff", "--name", "%s|%s" % (server1["name"], server2["name"]), "--wait")
    res = cloudcli("server", "info", "--name", "%s|%s" % (server1["name"], server2["name"]), parse=True)
    assert len(res) == 2
    assert res[0]["power"] == "off"
    assert res[1]["power"] == "off"
