import os
import pytest
import secrets
import datetime
import requests
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers, wait_command


def test_server_network_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server([session_server_powered_on, session_server_powered_off], "/server/network")


def test_server_network_no_matching_servers():
    assert_no_matching_servers("/server/network")


def test_server_network_list(session_server_powered_on):
    res = cloudcli_server_request("/server/network", method="POST", json={
        "name": session_server_powered_on["name"]
    })
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


def test_server_network_operations(temp_server, test_network):
    print("Get mac address")
    res = cloudcli_server_request("/server/network", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    mac_address = res[0]["mac"]
    print("mac address = %s" % mac_address)
    print("disconnect network")
    res = cloudcli_server_request("/server/network", method="POST", json={
        "name": temp_server["name"],
        "disconnect": mac_address
    })
    command_id = int(res)
    wait_command(command_id)
    res = cloudcli_server_request("/server/network", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert res[0]["connected"] == False
    print("connect network")
    res = cloudcli_server_request("/server/network", method="POST", json={
        "name": temp_server["name"],
        "connect": mac_address
    })
    command_id = int(res)
    wait_command(command_id)
    res = cloudcli_server_request("/server/network", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert res[0]["connected"] == True
    print("add network")
    res = cloudcli_server_request("/server/network", method="POST", json={
        "name": temp_server["name"],
        "add": test_network["name"],
        "ip": test_network["randomIp"],
        "subnet": "",
        "bits": "",
    })
    command_id = int(res)
    wait_command(command_id)
    res = cloudcli_server_request("/server/network", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 2
