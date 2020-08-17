import os
import random
import pytest
import requests
import tempfile
import subprocess
import json
import pexpect
from ruamel import yaml
from .common import terminate_fixture_server, create_fixture_server, wait_command, cloudcli_server_request, wait_for_res


class CloudcliFailedException(Exception):
    pass


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


@pytest.fixture(scope="session")
def session_server_sshkey():
    is_created_server, server = create_fixture_server("sshkey session server", "SESSION_SERVER_SSHKEY", sshkey=True)
    yield server
    if is_created_server:
        terminate_fixture_server("sshkey session server", "SESSION_SERVER_SSHKEY", server)


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
                    wait_for_res(
                        lambda: cloudcli_server_request("/service/server/info", method="POST", json={"name": server["server"]["name"], "allow-no-servers": "yes"}),
                        lambda res: len(res) > 0
                    )

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


def init_cloudcli_binary(tmpdir):
    if os.environ.get("CLOUDCLI_BINARY"):
        cloudcli_binary = os.environ["CLOUDCLI_BINARY"]
    else:
        subprocess.check_call(["curl", "-so", "cloudcli.tar.gz", "https://cloudcli.cloudwm.com/binaries/latest/cloudcli-linux-amd64.tar.gz"], cwd=tmpdir)
        subprocess.check_call(["tar", "-xzf", os.path.join(tmpdir, "cloudcli.tar.gz")], cwd=tmpdir)
        subprocess.check_call(["chmod", "+x", "cloudcli"], cwd=tmpdir)
        cloudcli_binary = "./cloudcli"
    if os.environ.get("CLOUDCLI_SCHEMA_FILE"):
        subprocess.check_call(["ln", "-s", os.environ["CLOUDCLI_SCHEMA_FILE"], os.path.join(tmpdir, ".cloudcli.schema.json")])
    else:
        subprocess.check_call([cloudcli_binary, "init", "--no-config"], cwd=tmpdir, env={
            "HOME": tmpdir,
            "CLOUDCLI_APICLIENTID": os.environ["KAMATERA_API_CLIENT_ID"],
            "CLOUDCLI_APISECRET": os.environ["KAMATERA_API_SECRET"],
            "CLOUDCLI_APISERVER": os.environ["KAMATERA_API_SERVER"],
        })
    return cloudcli_binary


@pytest.fixture(scope="session")
def cloudcli():
    with tempfile.TemporaryDirectory() as tmpdir:
        cloudcli_binary = init_cloudcli_binary(tmpdir)

        def _cloudcli(*args, ignore_wait_error=True, parse=False):
            args = list(args)
            if parse:
                if "--format" in args:
                    raise Exception("Cannot specify --format arg with parse=True")
                else:
                    args += ["--format", random.choice(("json", "yaml"))]
            try:
                output = subprocess.check_output([cloudcli_binary, *args], cwd=tmpdir, env={
                    "HOME": tmpdir,
                    "CLOUDCLI_APICLIENTID": os.environ["KAMATERA_API_CLIENT_ID"],
                    "CLOUDCLI_APISECRET": os.environ["KAMATERA_API_SECRET"],
                    "CLOUDCLI_APISERVER": os.environ["KAMATERA_API_SERVER"],
                }, stderr=subprocess.STDOUT).decode()
            except subprocess.CalledProcessError as exc:
                if "--wait" in args and ignore_wait_error:
                    print("WARNING! cloudcli failed but will continue anyway. exit code %s\n%s\n%s" % (exc.returncode, exc.output, exc.stderr))
                    return None
                else:
                    raise CloudcliFailedException("cloudcli failed exit code %s\n%s\n%s" % (exc.returncode, exc.output, exc.stderr))
            if "--format json" in  " ".join(args):
                output = json.loads(output)
            elif "--format yaml" in " ".join(args):
                output = yaml.safe_load(output)
            return output

        yield _cloudcli

@pytest.fixture(scope="session")
def cloudcli_pexpect():
    with tempfile.TemporaryDirectory() as tmpdir:
        cloudcli_binary = init_cloudcli_binary(tmpdir)

        def _cloudcli_pexpect(*args):
            return pexpect.spawn(cloudcli_binary, list(args), cwd=tmpdir, env={
                "HOME": tmpdir,
                "CLOUDCLI_APICLIENTID": os.environ["KAMATERA_API_CLIENT_ID"],
                "CLOUDCLI_APISECRET": os.environ["KAMATERA_API_SECRET"],
                "CLOUDCLI_APISERVER": os.environ["KAMATERA_API_SERVER"],
            })

        yield _cloudcli_pexpect
