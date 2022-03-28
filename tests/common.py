import os
import time
import requests
import datetime
import secrets
import pytest
import paramiko
import logging
import random


class WaitCommandErrorException(Exception):
    pass


class WaitResFailedException(Exception):
    pass


DEFAULT_FIXTURE_SERVER = {
    "datacenter": "IL",
    "image": "ubuntu_server_18.04_64-bit",
    "cpu": "1A",
    "ram": "1024",
    "disk": "size=10",
    "dailybackup": "no",
    "managed": "no",
    "network": "name=wan,ip=auto",
    "quantity": 1,
    "billingcycle": "hourly",
    "monthlypackage": "",
}


def cloudcli_server_request(path, ignore_errors=False, **kwargs):
    url = "%s%s" % (os.environ["KAMATERA_API_SERVER"], path)
    method = kwargs.pop("method", "GET")
    res = requests.request(method=method, url=url, headers={
        "AuthClientId": os.environ["KAMATERA_API_CLIENT_ID"],
        "AuthSecret": os.environ["KAMATERA_API_SECRET"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }, **kwargs)
    if res.status_code != 200:
        if ignore_errors:
            return res.status_code, res.json()
        else:
            raise Exception(res.json())
    else:
        if ignore_errors:
            return 200, res.json()
        else:
            return res.json()


def get_server_name():
    return "ktb-%s-%s" % (secrets.token_urlsafe(5), datetime.datetime.now().strftime("%Y%m%d%H%M"))


def get_server_password():
    return "Aa1!%s" % secrets.token_hex(12)


def wait_command(command_id, ignore_error=True):
    print("Waiting for command_id to complete %s" % command_id)
    wait_poll_interval_seconds = 2
    wait_timeout_seconds = 2400
    start_time = datetime.datetime.now()
    max_time = start_time + datetime.timedelta(seconds=wait_timeout_seconds)
    time.sleep(wait_poll_interval_seconds)
    command = {}
    i = 0
    while True:
        i += 1
        if max_time < datetime.datetime.now():
            if ignore_error:
                print("WARNING! Timeout waiting for command (timeout_seconds={0}, command_id={1})".format(
                    str(wait_timeout_seconds), str(command_id)
                ))
                return command
            else:
                raise Exception(
                    "Timeout waiting for command (timeout_seconds={0}, command_id={1})".format(
                        str(wait_timeout_seconds), str(command_id)
                    )
                )
        time.sleep(wait_poll_interval_seconds)
        command = get_command_status(command_id)
        printed_command = False
        if i in [1, 2, 3, 4, 5] or i % 10 == 0:
            printed_command = True
            print(command)
        status = command.get("status")
        if status == "complete":
            if not printed_command:
                print(command)
            print("command status == complete")
            return command
        elif status == "error":
            if not printed_command:
                print(command)
            print("command status == error")
            if ignore_error:
                print("WARNING! Command failed, but will continue anyway.\n%s" % command)
                return command
            else:
                raise WaitCommandErrorException("Command failed.\n%s" % command)
        elif status and status != "progress":
            if not printed_command:
                print(command)
            print("command status == %s" % status)


def wait_command_cloudcli(cloudcli, command_id, ignore_error=True):
    failed = False
    try:
        cloudcli("queue", "detail", "--id", str(command_id), "--wait", ignore_wait_error=False)
    except Exception:
        failed = True
    if failed:
        try:
            print(cloudcli("queue", "detail", "--id", str(command_id), "--format", "json"))
        except Exception:
            pass
        if not ignore_error:
            raise Exception("wait_command_cloudcli failed for command_id %s" % command_id)


def get_command_status(command_id):
    """Get a Kamatera command status"""
    response = cloudcli_server_request("/service/queue?id=" + str(command_id))
    if len(response) != 1:
        raise Exception("invalid response for command id " + str(command_id))
    return response[0]


def create_fixture_server(title, env_var_prefix, poweronaftercreate="yes", wait=True, sshkey=False):
    if os.environ.get("%s_NAME" % env_var_prefix):
        name = os.environ["%s_NAME" % env_var_prefix]
        print("Using existing %s %s" % (title, name))
        password = os.environ["%s_PASSWORD" % env_var_prefix] if not sshkey else ""
        create_server = False
    else:
        name = get_server_name()
        print("Creating %s %s" % (title, name))
        password = get_server_password() if not sshkey else ""
        create_server = True
    if sshkey:
        with open(os.environ["TESTING_SSHKEY_PATH"] + ".pub") as f:
            sshkey = f.read()
        private_sshkey_path = os.environ["TESTING_SSHKEY_PATH"]
    else:
        sshkey = ""
        private_sshkey_path = ""
    create_request_data = {
        "name": name,
        "password": password,
        "passwordValidate": password,
        "ssh-key": sshkey,
        **DEFAULT_FIXTURE_SERVER,
        "poweronaftercreate": poweronaftercreate,
    }
    command_id = None
    if create_server:
        res = cloudcli_server_request("/service/server", method="POST", json=create_request_data)
        print("%s create response: %s" % (title, res))
        command_id = int(res[0])
        if wait:
            wait_command(command_id)
            wait_for_res(
                lambda: cloudcli_server_request("/service/server/info", method="POST", json={"name": name, "allow-no-servers": "yes"}),
                lambda res: len(res) > 0
            )
            print("%s created" % title)
    return create_server, {
        "name": name, "password": password, "create_request_data": create_request_data, "command_id": command_id,
        "private_sshkey_path": private_sshkey_path
    }


def terminate_fixture_server(title, env_var_prefix, server):
    if os.environ.get("%s_KEEP" % env_var_prefix) == "yes":
        print("Keeping %s:" % title)
        print("export %s_NAME='%s'" % (env_var_prefix, server["name"]))
        print("export %s_PASSWORD='%s'" % (env_var_prefix, server["password"]))
    else:
        print("Removing %s %s" % (title, server["name"]))
        for _ in [1, 2, 3, 4, 5]:
            try:
                res = cloudcli_server_request("/service/server/terminate", method="POST", json={
                    "name": server["name"],
                    "force": True
                })
                print("terminate %s response: %s" % (title, res))
                return
            except Exception:
                logging.exception("Terminate server failed, will try again in 10 seconds")
                time.sleep(10)
        raise Exception("Failed to terminate server (%s %s)" % (title, server["name"]))


def assert_only_one_server(servers, path, extra_json=None):
    with pytest.raises(Exception, match="Too many matching servers"):
        cloudcli_server_request(path, method="POST", json={
            "name": "|".join([server["name"] for server in servers]),
            **(extra_json if extra_json else {})
        })


def assert_only_one_server_cloudcli(servers, cloudcli, args):
    with pytest.raises(Exception, match="Too many matching servers"):
        cloudcli(*args, "--name", "|".join([server["name"] for server in servers]))


def assert_no_matching_servers(path, extra_json=None):
    with pytest.raises(Exception, match="No servers found"):
        cloudcli_server_request(path, method="POST", json={
            "name": "__non_existent_server_name__",
            **(extra_json if extra_json else {})
        })


def assert_no_matching_servers_cloudcli(cloudcli, args):
    with pytest.raises(Exception, match="No servers found"):
        cloudcli(*args, "--name", "__non_existent_server_name__")


def get_server_id(server):
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": server["name"]
    })
    assert len(res) == 1
    return res[0]["id"]


def assert_server_ssh(server):
    res = cloudcli_server_request("/service/server/ssh", method="POST", json={
        "name": server["name"]
    })
    assert len(res) == 1
    assert set(res[0].keys()) == {"id", "name", "externalIp"}
    server_id = res[0]["id"]
    assert len(server_id) > 10
    assert res[0]["name"] == server["name"]
    server_external_ip = res[0]["externalIp"]
    for i in [0, 1, 2, 3, 4, 5]:
        if i > 0:
            time.sleep(10)
            print("Waited %s seconds" % (i * 10))
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        failed = False
        try:
            ssh_client.connect(server_external_ip, username="root", password=server["password"])
        except Exception:
            logging.exception("Failed to get SSH connection")
            failed = True
        if failed:
            print("Waiting for SSH connection (server name: %s)" % server["name"])
        else:
            assert ssh_client.exec_command("pwd")[1].read() == b'/root\n'
            return server_id, server_external_ip
    raise Exception("Waited too long for SSH (server name: %s)" % server["name"])


def wait_for_res(get_res, assert_res):
    for i in [0, 1, 2, 3, 4, 5]:
        if i > 0:
            time.sleep(10)
            print("Waited %s seconds" % (i * 10))
        res = get_res()
        if assert_res(res):
            return res
    raise WaitResFailedException()


def create_network(create_name):
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
    networks = requests.get(
        "https://console.kamatera.com/svc/networks/IL/networks?filter=%s&size=500&sorting=&from=" % create_name,
        headers=headers).json()["items"]
    assert len(networks) == 1
    network = networks[0]
    assert len(network["ids"]) == 1
    id = int(network["ids"][0])
    assert len(network["names"]) == 1
    name = network["names"][0]
    vlanId = int(network["vlanId"])
    subnets = requests.get("https://console.kamatera.com/svc/networks/subnets?datacenter=IL&vlanId=%s&filter=" % vlanId,
                           headers=headers).json()["subnets"]
    assert len(subnets) == 1
    subnet = subnets[0]
    subnetId = subnet["subnetId"]
    ips_json = requests.get("https://console.kamatera.com/svc/networks/ips?subnetId=%s&networkId=%s&datacenter=IL" % (subnetId, vlanId), headers=headers).json()
    availableIps = [ip["ip"] for ip in ips_json if not ip["clearIsEnable"]]
    return {
        "id": id, "name": name, "vlanId": vlanId, "subnetId": subnetId, "availableIps": availableIps,
        "randomIp": random.choice(availableIps)
    }


def assert_str_int(val):
    assert str(int(val)) == str(val)
    return int(val)
