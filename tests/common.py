import os
import time
import requests
import datetime
import secrets
import pytest
import paramiko


class WaitCommandErrorException(Exception):
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


def cloudcli_server_request(path, **kwargs):
    url = "%s%s" % (os.environ["KAMATERA_API_SERVER"], path)
    method = kwargs.pop("method", "GET")
    res = requests.request(method=method, url=url, headers={
        "AuthClientId": os.environ["KAMATERA_API_CLIENT_ID"],
        "AuthSecret": os.environ["KAMATERA_API_SECRET"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }, **kwargs)
    if res.status_code != 200:
        raise Exception(res.json())
    else:
        return res.json()


def get_server_name():
    return "ktb-%s-%s" % (secrets.token_urlsafe(5), datetime.datetime.now().strftime("%Y%m%d%H%M"))


def get_server_password():
    return "Aa1!%s" % secrets.token_hex(12)


def wait_command(command_id, ignore_error=True):
    print("Waiting for command_id to complete %s" % command_id)
    wait_poll_interval_seconds = 2
    wait_timeout_seconds = 1200
    start_time = datetime.datetime.now()
    max_time = start_time + datetime.timedelta(seconds=wait_timeout_seconds)
    time.sleep(wait_poll_interval_seconds)
    while True:
        if max_time < datetime.datetime.now():
            raise Exception(
                "Timeout waiting for command (timeout_seconds={0}, command_id={1})".format(
                    str(wait_timeout_seconds), str(command_id)
                )
            )
        time.sleep(wait_poll_interval_seconds)
        command = get_command_status(command_id)
        status = command.get("status")
        if status == "complete":
            return command
        elif status == "error":
            if ignore_error:
                print("WARNING! Command failed, but will continue anyway.\n%s" % command)
                return command
            else:
                raise WaitCommandErrorException("Command failed.\n%s" % command)


def get_command_status(command_id):
    """Get a Kamatera command status"""
    response = cloudcli_server_request("/service/queue?id=" + str(command_id))
    if len(response) != 1:
        raise Exception("invalid response for command id " + str(command_id))
    return response[0]


def create_fixture_server(title, env_var_prefix, poweronaftercreate="yes", wait=True):
    if os.environ.get("%s_NAME" % env_var_prefix) and os.environ.get("%s_PASSWORD" % env_var_prefix):
        name = os.environ["%s_NAME" % env_var_prefix]
        print("Using existing %s %s" % (title, name))
        password = os.environ["%s_PASSWORD" % env_var_prefix]
        create_server = False
    else:
        name = get_server_name()
        print("Creating %s %s" % (title, name))
        password = get_server_password()
        create_server = True
    create_request_data = {
        "name": name,
        "password": password,
        "passwordValidate": password,
        "ssh-key": "",
        **DEFAULT_FIXTURE_SERVER,
        "poweronaftercreate": poweronaftercreate,
    }
    command_id = None
    if create_server:
        res = cloudcli_server_request("/service/server", method="POST", json=create_request_data)
        print("%s create response: %s" % (title, res))
        command_id = int(res[0])
        if wait:
            wait_command(command_id, ignore_error=False)
            print("%s created" % title)
    return create_server, {"name": name, "password": password, "create_request_data": create_request_data, "command_id": command_id}


def terminate_fixture_server(title, env_var_prefix, server):
    if os.environ.get("%s_KEEP" % env_var_prefix) == "yes":
        print("Keeping %s:" % title)
        print("export %s_NAME='%s'" % (env_var_prefix, server["name"]))
        print("export %s_PASSWORD='%s'" % (env_var_prefix, server["password"]))
    else:
        print("Removing %s %s" % (title, server["name"]))
        res = cloudcli_server_request("/service/server/terminate", method="POST", json={
            "name": server["name"],
            "force": True
        })
        print("terminate %s response: %s" % (title, res))
        # command_id = int(res[0])
        # wait_command(command_id)
        # print("%s terminated" % title)


def assert_only_one_server(servers, path, extra_json=None):
    with pytest.raises(Exception, match="Too many matching servers"):
        cloudcli_server_request(path, method="POST", json={
            "name": "|".join([server["name"] for server in servers]),
            **(extra_json if extra_json else {})
        })


def assert_no_matching_servers(path, extra_json=None):
    with pytest.raises(Exception, match="No servers found"):
        cloudcli_server_request(path, method="POST", json={
            "name": "__non_existent_server_name__",
            **(extra_json if extra_json else {})
        })


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
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(server_external_ip, username="root", password=server["password"])
    assert ssh_client.exec_command("pwd")[1].read() == b'/root\n'
    return server_id, server_external_ip
