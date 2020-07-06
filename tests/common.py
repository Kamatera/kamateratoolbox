import os
import time
import requests
import datetime
import secrets
import pytest


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


def wait_command(command_id):
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
            raise Exception("Command failed: " + command.get("log"))


def get_command_status(command_id):
    """Get a Kamatera command status"""
    response = cloudcli_server_request("/service/queue?id=" + str(command_id))
    if len(response) != 1:
        raise Exception("invalid response for command id " + str(command_id))
    return response[0]


def create_fixture_server(title, env_var_prefix, poweronaftercreate="yes"):
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
    if create_server:
        res = cloudcli_server_request("/service/server", method="POST", json=create_request_data)
        print("%s create response: %s" % (title, res))
        command_id = int(res[0])
        wait_command(command_id)
        print("%s created" % title)
    return create_server, {"name": name, "password": password, "create_request_data": create_request_data}


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


def assert_only_one_server(path):
    with pytest.raises(Exception, match="Too many matching servers"):
        cloudcli_server_request(path, method="POST", json={
            "name": ".*"
        })


def assert_no_matching_servers(path):
    with pytest.raises(Exception, match="No servers found"):
        cloudcli_server_request(path, method="POST", json={
            "name": "__non_existent_server_name__"
        })
