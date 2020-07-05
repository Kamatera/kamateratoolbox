import pytest
import paramiko
from ..common import cloudcli_server_request, assert_only_one_server, assert_no_matching_servers


def test_server_attach_only_one_server(session_server_powered_on, session_server_powered_off):
    assert_only_one_server("/service/server/ssh")


def test_server_attach_no_matching_servers():
    assert_no_matching_servers("/service/server/ssh")


def test_server_attach(session_server_powered_on):
    res = cloudcli_server_request("/service/server/ssh", method="POST", json={
        "name": session_server_powered_on["name"]
    })
    assert len(res) == 1
    assert set(res[0].keys()) == {"id", "name", "externalIp"}
    assert len(res[0]["id"]) > 10
    assert res[0]["name"] == session_server_powered_on["name"]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(res[0]["externalIp"], username="root", password=session_server_powered_on["password"])
    assert ssh_client.exec_command("pwd")[1].read() == b'/root\n'
