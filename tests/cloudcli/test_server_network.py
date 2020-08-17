import pytest
import time
from ..common import assert_only_one_server_cloudcli, assert_no_matching_servers_cloudcli, get_server_id, wait_for_res, wait_command_cloudcli


def test_server_network_only_one_server(cloudcli, session_server_powered_on, session_server_powered_off):
    assert_only_one_server_cloudcli([session_server_powered_on, session_server_powered_off], cloudcli, ["server", "network"])


def test_server_network_no_matching_servers(cloudcli):
    assert_no_matching_servers_cloudcli(cloudcli, ["server", "network"])


def test_server_network_list(cloudcli, session_server_powered_on):
    for res in [cloudcli("server", "network", "--name", session_server_powered_on["name"], "--format", "json"),
                cloudcli("server", "network", "--name", session_server_powered_on["name"], "--format", "yaml")]:
        assert len(res) == 1
        res = res[0]
        assert set(res.keys()) == {"network", "connected", "mac", "ips", "routedIps", "manualConfigEnabled", "actions"}
        assert res["network"] == "wan-il"
        assert res["connected"] == True
        assert len(res["mac"]) > 5
        assert len(res["ips"]) == 1
        assert len(res["routedIps"]) == 0
        assert res["manualConfigEnabled"] == False
        assert set(res["actions"].keys()) == {"nic.disconnect", "nic.connect", "nic.ip.remove", "nic.ip.add", "nic.change", "nic.remove", "nic.info"}
        assert all((isinstance(v, bool) for v in res["actions"].values()))


def test_server_network_list_by_id(cloudcli, session_server_powered_on):
    for res in [cloudcli("server", "network", "--id", get_server_id(session_server_powered_on), "--format", "json"),
                cloudcli("server", "network", "--id", get_server_id(session_server_powered_on), "--format", "yaml")]:
        assert len(res) == 1
        assert set(res[0].keys()) == {"network", "connected", "mac", "ips", "routedIps", "manualConfigEnabled", "actions"}


def test_server_network_operations(cloudcli, temp_server, test_network):
    print("Get mac address")
    res = cloudcli("server", "network", "--name", temp_server["name"], parse=True)
    assert len(res) == 1
    mac_address = res[0]["mac"]
    print("mac address = %s" % mac_address)
    print("disconnect network")
    cloudcli("server", "network", "--name", temp_server["name"], "--disconnect", mac_address, "--wait")
    res = cloudcli("server", "network", "--name", temp_server["name"], parse=True)
    assert len(res) == 1
    assert res[0]["connected"] == False
    print("connect network")
    res = cloudcli("server", "network", "--name", temp_server["name"], "--connect", mac_address, "--format", "yaml")
    command_id = int(res)
    # TODO: figure out how to reliably test this condition as the time until operation starts and ends is not reliable
    # print("sleeping 3 seconds to ensure connect operation is running before testing existing operation running error")
    # time.sleep(3)
    # with pytest.raises(Exception, match="Existing operation is currently running"):
    #     cloudcli("server", "network", "--name", temp_server["name"])
    wait_command_cloudcli(cloudcli, command_id)
    res = cloudcli("server", "network", "--name", temp_server["name"], parse=True)
    assert len(res) == 1
    assert res[0]["connected"] == True
    print("add network")
    cloudcli("server", "network", "--name", temp_server["name"], "--add", test_network["name"], "--ip", test_network["randomIp"], "--wait")
    res = wait_for_res(lambda: cloudcli("server", "network", "--name", temp_server["name"], parse=True), lambda res: len(res) == 2)
    assert len(res) == 2
