import pytest
from ..common import cloudcli_server_request, assert_no_matching_servers, get_server_id, get_server_password, wait_command, assert_server_ssh


def test_server_configure_errors(session_server_powered_on, session_server_powered_off):
    with pytest.raises(Exception, match="Please choose a configuration flag"):
        cloudcli_server_request("/server/configure", method="POST", json={
            "name": "__non_existent_server__"
        })
    with pytest.raises(Exception, match="--name flag did not match any servers"):
        cloudcli_server_request("/server/configure", method="POST", json={
            "name": "__non_existent_server__",
            "cpu": "AA"
        })
    with pytest.raises(Exception, match="Please choose only 1 configuration flag at a time"):
        cloudcli_server_request("/server/configure", method="POST", json={
            "name": "__non_existent_server__",
            "cpu": "AA",
            "ram": "BB"
        })
    with pytest.raises(Exception, match="Please choose --id or --name flags"):
        cloudcli_server_request("/server/configure", method="POST", json={
            "name": "__non_existent_server__",
            "id": "__non_existent_server_id__",
            "cpu": "AA",
        })
    with pytest.raises(Exception, match="--name flag must match a single server"):
        cloudcli_server_request("/server/configure", method="POST", json={
            "name": "%s|%s" % (session_server_powered_on["name"], session_server_powered_off["name"]),
            "cpu": "AA",
        })


def test_server_configure(temp_server):
    print("Configuring server CPU")
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert res[0]["cpu"] == "1A"
    res = cloudcli_server_request("/server/configure", method="POST", json={
        "name": temp_server["name"],
        "cpu": "2A"
    })
    assert len(res) == 1
    wait_command(res[0])
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert res[0]["cpu"] == "2A"
    print("Configuring server RAM")
    assert res[0]["ram"] == 1024
    res = cloudcli_server_request("/server/configure", method="POST", json={
        "name": temp_server["name"],
        "ram": "2048"
    })
    assert len(res) == 1
    wait_command(res[0])
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert res[0]["ram"] == 2048
    print("Configuring server dailybackup")
    assert res[0]["backup"] == "0"
    res = cloudcli_server_request("/server/configure", method="POST", json={
        "name": temp_server["name"],
        "dailybackup": "yes"
    })
    assert len(res) == 1
    wait_command(res[0])
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert res[0]["backup"] == "1"
    print("Configuring server managed")
    assert res[0]["managed"] == "0"
    res = cloudcli_server_request("/server/configure", method="POST", json={
        "name": temp_server["name"],
        "managed": "yes"
    })
    assert len(res) == 1
    wait_command(res[0])
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert res[0]["managed"] == "1"
    print("Configuring server billingcycle")
    assert res[0]["billing"] == "hourly"
    res = cloudcli_server_request("/server/configure", method="POST", json={
        "name": temp_server["name"],
        "billingcycle": "monthly",
        "monthlypackage": "t5000"
    })
    assert len(res) == 1
    wait_command(res[0])
    res = cloudcli_server_request("/service/server/info", method="POST", json={
        "name": temp_server["name"]
    })
    assert len(res) == 1
    assert res[0]["billing"] == "monthly"
