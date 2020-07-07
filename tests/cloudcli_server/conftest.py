import os
import random
import pytest
import requests
from ..common import terminate_fixture_server, create_fixture_server, wait_command


@pytest.fixture(scope="session")
def session_server_powered_on():
    is_created_server, server = create_fixture_server("powered on session server", "SESSION_SERVER_POWERED_ON")
    yield server
    if is_created_server:
        terminate_fixture_server("powered on session server", "SESSION_SERVER_POWERED_ON", server)


@pytest.fixture(scope="session")
def session_server_powered_off():
    is_created_server, server = create_fixture_server("powered off session server", "SESSION_SERVER_POWERED_OFF", poweronaftercreate="no")
    yield server
    if is_created_server:
        terminate_fixture_server("powered off session server", "SESSION_SERVER_POWERED_OFF", server)


@pytest.fixture()
def temp_server():
    is_created_server, server = create_fixture_server("temp server", "TEMP_SERVER")
    yield server
    if is_created_server:
        terminate_fixture_server("temp server", "TEMP_SERVER", server)


@pytest.fixture()
def temp_servers_factory():
    servers = {}

    def _temp_servers_factory(command):
        if command == "create":
            server_num = len(servers) + 1
            is_created_server, server = create_fixture_server("temp server %s" % server_num, "TEMP_SERVER_%s" % server_num, wait=False)
            servers[server_num] = {"is_created": is_created_server, "server": server}
            return server
        elif command == "wait":
            for server in servers.values():
                if server["server"]["command_id"]:
                    wait_command(server["server"]["command_id"])

    yield _temp_servers_factory
    for server_num, server in servers.items():
        if server["is_created"]:
            terminate_fixture_server("temp server %s" % server_num, "TEMP_SERVER_%s" % server_num, server["server"])


@pytest.fixture()
def test_network():
    create_name = "ktb-testnet"
    headers = {
        "AuthClientId": os.environ["KAMATERA_API_CLIENT_ID"],
        "AuthSecret": os.environ["KAMATERA_API_SECRET"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print("create network for testing: %s" % create_name)
    requests.request(method="POST", url="https://console.kamatera.com/svc/networks/IL/create", headers=headers, json={
        "name": create_name,
        "subnetIp": "172.16.0.0",
        "subnetBit": 23,
        "gateway": "",
        "dns1": "",
        "dns2": ""
    })
    networks = requests.get("https://console.kamatera.com/svc/networks/IL/networks?filter=%s&size=500&sorting=&from=" % create_name, headers=headers).json()["items"]
    assert len(networks) == 1
    network = networks[0]
    assert len(network["ids"]) == 1
    id = int(network["ids"][0])
    assert len(network["names"]) == 1
    name = network["names"][0]
    vlanId = int(network["vlanId"])
    subnets = requests.get("https://console.kamatera.com/svc/networks/subnets?datacenter=IL&vlanId=%s&filter=" % vlanId, headers=headers).json()["subnets"]
    assert len(subnets) == 1
    subnet = subnets[0]
    subnetId = subnet["subnetId"]
    availableIps = [ip["ip"] for ip in requests.get("https://console.kamatera.com/svc/networks/ips?subnetId=%s" % subnetId, headers=headers).json() if not ip["clearIsEnable"]]
    yield {"id": id, "name": name, "vlanId": vlanId, "subnetId": subnetId, "availableIps": availableIps, "randomIp": random.choice(availableIps)}
